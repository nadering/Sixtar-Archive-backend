# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views import View
from django.db.models import Q, F

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions

import copy

from api.models import Music, Dlc, MusicPack, Pattern, PatternHistory
from api.serializers import MusicSerializer, DlcSerializer, MusicPackSerializer, PatternSerializer, BoardSerializer, PatternHistorySerializer


class MusicListAPI(APIView):
  def get(self, request):
    queryset = Music.objects.all()
    serializer = MusicSerializer(queryset, many=True)
    return Response(serializer.data)
  
  
class DlcListAPI(APIView):
  def get(self, request):
    queryset = Dlc.objects.all()
    serializer = DlcSerializer(queryset, many=True)
    return Response(serializer.data)
  
  
class MusicPackListAPI(APIView):
  def get(self, request):
    queryset = MusicPack.objects.all()
    serializer = MusicPackSerializer(queryset, many=True)
    return Response(serializer.data)
  
  
class PatternListAPI(APIView):
  def get(self, request):
    queryset = Pattern.objects.all()
    serializer = PatternSerializer(queryset, many=True)
    return Response(serializer.data)


class BoardAPI(APIView):
  def get(self, request):
    # URL: board?(mode=lunar|solar min=1~17 max=1~17 type=comet|nova|supernova|quasar|starlight)
    mode_list = ['lunar', 'solar']
    difficulty_type_list = ['comet', 'nova', 'supernova', 'quasar', 'starlight']
    
    # 모드 확인
    if not 'mode' in request.GET:
      raise exceptions.ParseError(f"모드 정보를 찾을 수 없습니다. (mode={('|').join(mode_list)})")
    else:
      if (mode := request.GET['mode']) not in mode_list:
        raise exceptions.ParseError(f"잘못된 모드가 입력되었습니다. (mode={('|').join(mode_list)})")
    
    # 사용자가 입력한 난이도 최소/최대치 및 난이도 종류 확인
    is_number, user_min_num, user_max_num, is_diff_type, user_diff_type = self._analyzeRequest(request, difficulty_type_list)
    
    # GET에서 요구하는 내용을 DB에서 가져옴
    # query_result: {'type_1': [patterns], 'type_2': [patterns], ... }
    query_result = {}
    if is_number:
      if is_diff_type:
        query_result[user_diff_type] = self._getNumberTypeResult(mode, user_diff_type, user_min_num, user_max_num)
      else:
        for diff_type in difficulty_type_list:
          query_result[diff_type] = self._getNumberTypeResult(mode, diff_type, user_min_num, user_max_num)
    elif is_diff_type:
      query_result[user_diff_type] = self._getDifficultyTypeResult(mode, user_diff_type)
    else:
      raise exceptions.ParseError(f"잘못된 정보가 입력되었거나, 입력된 정보가 부족합니다. (min=<int>&max=<int> | type={('|').join(difficulty_type_list)})")
    
    for patterns in query_result.values():
      for pattern in patterns:
        pattern.update(self._getMusicInfo(pattern['music_id']))
    
    # 결과물을 JSON으로 바꾸기 위해 포매팅
    board_data = []
    min_diff = 99
    max_diff = -1
    pattern_count = 0
    for diff_type, patterns in query_result.items():
      # pattern: 패턴
      # {music_id, difficulty, floor, name, composer, dlc_id, dlc_name, music_pack_id, music_pack_name, bpm, bpm_min, bpm_max}
      for pattern in patterns:
        pattern_count += 1
        
        if len(board_data) == 0:
          self._addDifficultyToData(board_data, diff_type, pattern)
        else:
          # board_data: diff_dict가 담겨있는 곳
          # diff_dict: 난이도, [층과 층마다 구분된 패턴들] (ex: 15.1, 15.2, ...)
          pattern_added = False
          for diff_dict in board_data:
            if diff_dict['difficulty'] == pattern['difficulty']:
              # floor_dict: 층, 층별 패턴 (ex: 15.3)
              # 현재 패턴의 층수가 이미 데이터에 존재하는지 확인한 후, 존재한다면 패턴을 추가
              for floor_dict in diff_dict['floors']:
                if floor_dict['floor'] == pattern['floor']:
                  self._addPatternToData(floor_dict['patterns'], diff_type, pattern)
                  pattern_added = True
                  break  
              if pattern_added:
                break
              else:
                # 현재 패턴의 층수에 해당하는 층수가 데이터에 없다면,
                # 새로 층수를 만들며 패턴을 추가 (ex: 패턴이 15.1층, 데이터에 15레벨은 있지만 15.1층이 없는 경우)
                self._addFloorToData(diff_dict['floors'], diff_type, pattern)
                pattern_added = True
                break   
          if not pattern_added:
            # 현재 패턴의 난이도에 해당하는 난이도가 데이터에 없다면, 
            # 새로 난이도와 층수를 만들며 패턴을 추가 (ex: 패턴이 14레벨, 14레벨이 데이터에 없음)
            self._addDifficultyToData(board_data, diff_type, pattern)
    
    # Decimal -> Float 변환, 미분류된 층수 설정, 데이터 정렬
    for diff_dict in board_data:
      # null인 floor는 해당 난이도의 0층으로 설정 (1층보다 쉽다는 것이 아니라, 미분류를 의미함)
      for floor_dict in diff_dict['floors']:
        try:
          floor_dict['floor'] = float(floor_dict['floor'])
        except TypeError:
          floor_dict['floor'] = float(diff_dict['difficulty'])
    
    # 정렬할 때 x['difficulty'], x['floor'] 앞에 -가 붙으면 내림차순, 없으면 오름차순
    board_data = sorted(board_data, key=lambda x: x['difficulty'])
    for diff_dict in board_data:
      if min_diff > diff_dict['difficulty']:
        min_diff = diff_dict['difficulty']
      if max_diff < diff_dict['difficulty']:
        max_diff = diff_dict['difficulty']
      diff_dict['floors'] = sorted(diff_dict['floors'], key=lambda x: x['floor'])
    
    # JSON으로 데이터 반환
    result_data = {
      'mode': mode,
      'min_difficulty': min_diff,
      'max_difficulty': max_diff,
      'pattern_count': pattern_count,
      'board': board_data
    }
    board_serializer = BoardSerializer(result_data)
    
    return Response(board_serializer.data, status=200)
  
  # Parses request (GET method)
  def _analyzeRequest(self, request, diff_type_list: list):
    is_number, user_min_num, user_max_num = self._analyzeNumberType(request)
    is_diff_type, user_diff_type = self._analyzeDifficultyType(request, diff_type_list)
    return is_number, user_min_num, user_max_num, is_diff_type, user_diff_type
  
  def _analyzeNumberType(self, request):
    if 'min' in request.GET and 'max' in request.GET:
      try:
        min_num = int(request.GET['min'])
        max_num = int(request.GET['max'])
      except ValueError:
        raise exceptions.ParseError("잘못된 타입의 난이도가 입력되었습니다. (min=<int>&max=<int>)")
      except Exception as e:
        raise exceptions.ParseError(e)
      if min_num > max_num:
        raise exceptions.ParseError("잘못된 난이도가 입력되었습니다. (최소 난이도가 최대 난이도보다 높습니다.)")
      return True, min_num, max_num
    elif 'min' in request.GET or 'max' in request.GET:
      raise exceptions.ParseError("잘못된 난이도가 입력되었습니다. (최소 난이도와 최대 난이도를 모두 입력해야 합니다.)")
    else:
      return False, 0, 0
  
  def _analyzeDifficultyType(self, request, diff_type_list: list):
    if 'type' in request.GET:
      difficulty_type = request.GET['type']
      if difficulty_type not in diff_type_list:
        raise exceptions.ParseError(f"잘못된 난이도 종류가 입력되었습니다. (type={('|').join(diff_type_list)}")
      return True, difficulty_type
    else:
      return False, ""
  
  # Selects data from DB
  def _getNumberTypeResult(self, mode: str, diff_type: str, min_num: int, max_num: int):
    difficulty_name = f'{mode}_{diff_type}'
    floor_name = f'{mode}_f_{diff_type}'
    
    query_result = Pattern.objects.alias(
      difficulty=F(difficulty_name), floor=F(floor_name)).annotate(
        difficulty=F(difficulty_name), floor=F(floor_name)
      ).select_related(
        'music'
      ).filter(
        (Q(difficulty__gte=min_num) & Q(difficulty__lte=max_num)) |
        (Q(floor__gte=min_num) & Q(floor__lt=max_num+1))
      ).annotate(
        name=F('music__name'), composer=F('music__composer'),
        bpm=F('music__bpm'), bpm_min=F('music__bpm_min'), bpm_max=F('music__bpm_max'),
      ).order_by(
        '-difficulty', '-floor', 'name'
      ).values(
        'music_id', 'difficulty', 'floor', 'name', 'composer', 'bpm', 'bpm_min', 'bpm_max'
      )
    
    return list(query_result)
  
  def _getDifficultyTypeResult(self, mode: str, diff_type: str):
    difficulty_name = f'{mode}_{diff_type}'
    floor_name = f'{mode}_f_{diff_type}'
    
    query_result = Pattern.objects.alias(
      difficulty=F(difficulty_name), floor=F(floor_name)).annotate(
        difficulty=F(difficulty_name), floor=F(floor_name)
      ).select_related(
        'music'
      ).filter(
        difficulty__isnull=False
      ).annotate(
        name=F('music__name'), composer=F('music__composer'),
        bpm=F('music__bpm'), bpm_min=F('music__bpm_min'), bpm_max=F('music__bpm_max'),
      ).order_by(
        '-difficulty', '-floor', 'name'
      ).values(
        'music_id', 'difficulty', 'floor', 'name', 'composer', 'bpm', 'bpm_min', 'bpm_max'
      )
      
    return list(query_result)
  
  def _getMusicInfo(self, music_id: int):
    query_result = Music.objects.select_related(
      'dlc'
    ).select_related(
      'musicpack'
    ).annotate(
      dlc_name=F('dlc__name'), dlc_code=F('dlc__code'),
      music_pack_name=F('music_pack__name')
    ).filter(id=music_id).values(
      'dlc_name', 'dlc_code', 'music_pack_name', 'music_pack_id'
    )
    
    return list(query_result)[0]
  
  # Makes board data, and helps eleborate it to Json.
  def _makePatternData(self, diff_type, pattern):
    pattern_dict = copy.deepcopy(pattern)
    pattern_dict['type'] = diff_type
    del(pattern_dict['difficulty'])
    del(pattern_dict['floor'])
    
    return pattern_dict
  
  def _addPatternToData(self, data, diff_type, pattern):
    data.append(self._makePatternData(diff_type, pattern))
  
  def _addFloorToData(self, data, diff_type, pattern):
    floor_dict = {
      'floor': pattern['floor'],
      'patterns': []
    }
    
    self._addPatternToData(floor_dict['patterns'], diff_type, pattern)
    data.append(floor_dict)
  
  def _addDifficultyToData(self, data, diff_type, pattern):
    diff_dict = {
      'difficulty': pattern['difficulty'],
      'floors': []
    }
    
    self._addFloorToData(diff_dict['floors'], diff_type, pattern)
    data.append(diff_dict)
  

class PatternHistoryListAPI(APIView):
  def get(self, request):
    queryset = PatternHistory.objects.all()
    serializer = PatternHistorySerializer(queryset, many=True)
    return Response(serializer.data)
