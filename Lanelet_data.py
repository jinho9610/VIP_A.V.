#-*- coding:utf-8 -*-
import matplotlib.pyplot as plt
import sys
import math
sys.path.append("C:/Users/Junhyeok/Desktop/test/map")

# try:
#     import get_map_data
# except ImportError:
#     raise



#파일 탐색하는 함수 : 키보드 입력으로 넣어준 레인이 있는지 확인함. 
def get_lane_num():
	while True:
		get_lane = input('enter proper lane ID:')
		LaneData = None
		for i in get_map_data.final_data_cand:
			if i['id'] == get_lane:
				LaneData = i
				print('proper ID')
				break

		if LaneData is not None:
			break

	return LaneData


#레인 2개 입력하면 합쳐주는 함수
def combine_two_lane(Lane1,Lane2):

	# print(Lane1['pre_lane'])
	# print(Lane1['next_lane'])
	# print(Lane2['next_lane'])
	# print(Lane2['pre_lane'])
	# print('lane1 id is {}'.format(Lane1['id']))
	# print(Lane2['id'])
	# print(type((Lane2['id'])))

	temp1 = Lane1['id']
	temp1 = int(temp1)
	temp2 = Lane2['id']
	temp2 = int(temp2)
	

	#it can be reduced by half 

	# 경우의 수 2가지 ㄷ
	# lane1 -> lane2
	det1 = set(Lane1['next_lane']) & set([temp2])
	det2 = set([temp1]) & set(Lane2['pre_lane'])
	# lane2 -> lane1
	det3 = set(Lane1['pre_lane']) & set([temp2])
	det4 = set([temp1]) & set(Lane2['next_lane'])

	# print(det1)
	# print(det2)
	# print(det3)
	# print(det4)
	if (abs(Lane1['x'][-1] - Lane2['x'][0])>1.5) or (abs(Lane1['y'][-1] - Lane2['y'][0])>1.5):
		print('오류 : ',Lane1['id'],' ',Lane2['id'])
		c=0
		j=0
		i=0
		l=0
		while True:
			x1=Lane2['x'][i]
			x2=Lane1['x'][-1]
			y1=Lane2['y'][i]
			y2=Lane1['y'][-1]
			if x1==Lane2['x'][-1] and y1==Lane2['y'][-1]:
				l=i
				break
			d = float(math.sqrt((float(abs(x1-x2)) * float(abs(x1-x2)) + float((abs(y1-y2)) * float(abs(y1-y2))))))
			if i==0 or (c>=d):
				c=d
				j=i
			i=i+1
		if c>2:
			print('제작 오류')
			return 999,0,0,0,0
		elif  l-j>100 :
			print('최소거리 : ',c,'  전체 길이 ',l,'중에 ',' {}번째 줄까지 지우세요!'.format(j))
			return 0,999,0,0,0
		return 0,0,0,0,0
	if (len(det1) == 1) or (len(det2) == 1):
		x = Lane1['x'] + Lane2['x']
		y = Lane1['y'] + Lane2['y']
		yaw = Lane1['yaw'] + Lane2['yaw']
		k = Lane1['k'] + Lane2['k']
		s = Lane1['s'] + Lane2['s']

	elif (len(det3) ==1) or (len(det4) ==1):
		x = Lane2['x'] + Lane1['x']
		y = Lane2['y'] + Lane1['y']
		yaw = Lane2['yaw'] + Lane1['yaw']
		k = Lane2['k'] + Lane1['k']
		s = Lane2['s'] + Lane1['s']

	else:
		x = []
		y = []
		yaw = []
		k = []
		s = []
		print('imposible to connect lane')

	return x, y, yaw, k, s




if __name__ == "__main__":
	lane1 = get_lane_num()
	lane2 = get_lane_num()

	cx, cy, cyaw, ck, cs = combine_two_lane(lane1, lane2)


	plt.plot(cx, cy)
	plt.scatter(cx, cy, marker='.')

	plt.show()

	


