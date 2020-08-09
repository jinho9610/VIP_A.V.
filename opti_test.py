#-*- coding:utf-8 -*-
import glob
import copy
import matplotlib.pyplot as plt 
from Lanelet_data import combine_two_lane



def cur_postion():
  data, sender = sock.recvfrom(1024)
  data = data.decode()
  GGA_msg =pynmea2.parse(data.split('\n')[1])

  lat = str(float(GGA_msg.lat[0:2]) + (float(GGA_msg.lat[2:9])/60))
  lon = str(float(GGA_msg.lon[0:3]) + (float(GGA_msg.lon[3:10])/60))
  cur_x, cur_y = get_xy(float(lat), float(lon), GGA_msg.altitude)
  return cur_x, cur_y

def visitPlace(visit,path,MAP):
  path[visit]['visited'] = 1
  for toGo, betweenDist in MAP[visit].items():
    toDist = path[visit]['shortestDist'] + betweenDist
    if (path[toGo]['shortestDist'] >= toDist) or  not path[toGo]['route']:
      path[toGo]['shortestDist'] = toDist
      path[toGo]['route'] = copy.deepcopy(path[visit]['route'])
      path[toGo]['route'].append(visit)
              

def final(departure,path ,destination,x,num):
  i=0
  cx=[]
  cy=[]
  cyaw=[]
  ck=[]
  cs=[]
  
  id1=departure
  #print(id1)
  
  
  if num==1:
    cx=x['x']
    cy=x['y']
    cyaw=x['yaw']
    ck=x['k']
    cs=x['s']
    id1='Lane1001'
  
  while True :
    value=path[destination]['route'][i]
    '''
    if i is not 0:
      cx[-1]=globals()['{}'.format(value)]['x'][0]
      cy[-1]=globals()['{}'.format(value)]['y'][0]
   '''
    cx=cx+globals()['{}'.format(value)]['x']
    cy=cy+globals()['{}'.format(value)]['y']
    cyaw=cyaw+globals()['{}'.format(value)]['yaw']
    ck=ck+globals()['{}'.format(value)]['k']
    cs=cs+globals()['{}'.format(value)]['s']
    # plt.plot(cx,cy)
    # plt.scatter(cx,cy)
    # plt.title( globals()['{}'.format(value)]['id'])
    # plt.show()
    if value==path[destination]['route'][-1]:
      break
  
    i=i+1
  cx=cx+globals()['{}'.format(destination)]['x']
  cy=cy+globals()['{}'.format(destination)]['y']
  cyaw=cyaw+globals()['{}'.format(destination)]['yaw']
  ck=ck+globals()['{}'.format(destination)]['k']
  cs=cs+globals()['{}'.format(destination)]['s']
  
  plt.plot(cx,cy)
  plt.scatter(cx,cy)
  plt.title( globals()['{}'.format(destination)]['id'])
  plt.show()
  
  globals()['Lane{}'.format(9999)] = {'id': 9999,'x':[], 'y':[], 'yaw':[], 'k':[],'s':[], 'pre_lane': [], 'next_lane': []}
  globals()['Lane{}'.format('9999')]['x']=cx
  globals()['Lane{}'.format('9999')]['y']=cy
  globals()['Lane{}'.format('9999')]['yaw']=cyaw
  globals()['Lane{}'.format('9999')]['k']=ck
  globals()['Lane{}'.format('9999')]['s']=cs

  return globals()['Lane{}'.format('9999')]

def make_line(x1, y1):
  files = glob.glob('*.txt') #현재 디텍토리 내의 모든 txt 파일 저장 리스트로 저장되는 거 같음.
  final_data_cand = [] # 이거는 그냥 임시용 전체 파일 볼일이 있을까봐 만듦. 당장은 필요 없음
  MAP={}

  for file in files:
     # 파일명이 1001.txt 아니면 2031R.txt 이런 식으로 8자리 아니면 9자리니까 .txt 앞부분 이름만 저장하기 위해서 경우 나눔.
     if len(file) == 8:
        temp_name = file[0:4]
     elif len(file) ==9:
        temp_name = file[0:4]
     else:
        pass

     temp_name2 = file[0:4] # id는 숫자로만 구성하기로함. 
     #동적 변수 생성한는 건데 for 문 돌면서 파일명에 따른 변수명 만들고 id, x,  y ,yaw, k, s, pre_lane, next_lane이 들어있는
     # 딕셔너리를 만듦.  메모장 파일 이름이 1001.txt 이면 변수는 Lane1001로 저장됨.
     globals()['Lane{}'.format(temp_name)] = {'id': temp_name2,'x':[], 'y':[], 'yaw':[], 'k':[],
     's':[], 'pre_lane': [], 'next_lane': []}
     MAP['Lane{}'.format(temp_name)]={}
     # print(globals()['Lane{}'.format(temp_name)])

     # x y yaw k s 값 저장해줌.
     f = open(file,'r')

     while True:
        line = f.readline()
        if not line:
           break

        globals()['Lane{}'.format(temp_name)]['x'].append(float(line.split()[0]))
        globals()['Lane{}'.format(temp_name)]['y'].append(float(line.split()[1]))
        globals()['Lane{}'.format(temp_name)]['yaw'].append(float(line.split()[2]))
        globals()['Lane{}'.format(temp_name)]['k'].append(float(line.split()[3]))
        globals()['Lane{}'.format(temp_name)]['s'].append(float(line.split()[4]))

     final_data_cand.append(globals()['Lane{}'.format(temp_name)])

     f.close()

  # print(final_data_cand)
  # Lane기록일지 참고해서 직접 이후레인 이전레인 append 해줌
  def nearest_dpt_lane(x1, y1):
    dst_Xpoint,dst_Ypoint = x1, y1
    print(dst_Xpoint)
    print(dst_Ypoint)
    
    min_dst_cand = []
    for lane in final_data_cand:

      delta_X  = [dst_Xpoint - ix for ix in lane['x']]
      delta_Y  = [dst_Ypoint - iy for iy in lane['y']]
      dst = [idelx ** 2 + idely ** 2 for (idelx, idely) in zip(delta_X, delta_Y)]
      min_dst = min(dst)
      min_dst_cand.append(min_dst)
     
    min_dst = min(min_dst_cand)
    idx = min_dst_cand.index(min_dst)
    return final_data_cand[idx]['id']

  def nearest_dst_lane():
    dst_Xpoint = float(input('enter X: '))
    dst_Ypoint = float(input('enter Y: '))

    min_dst_cand = []
    for lane in final_data_cand:

      delta_X  = [dst_Xpoint - ix for ix in lane['x']]
      delta_Y  = [dst_Ypoint - iy for iy in lane['y']]
      dst = [idelx ** 2 + idely ** 2 for (idelx, idely) in zip(delta_X, delta_Y)]
      min_dst = min(dst)
      min_dst_cand.append(min_dst)
     
    min_dst = min(min_dst_cand)
    idx = min_dst_cand.index(min_dst)
    return final_data_cand[idx]['id']

  Lane1001['next_lane'].append(2003)
  Lane1001['next_lane'].append(2103)
  Lane1001['next_lane'].append(2203)
  MAP['Lane1001']={'Lane2003':Lane2003['s'][-1]},{'Lane2103':Lane2103['s'][-1]},{'Lane2203':Lane2203['s'][-1]}

  Lane1002['pre_lane'].append(2004)
  Lane1002['pre_lane'].append(2104)
  Lane1002['pre_lane'].append(2204)


  # segment 2 (1)우회전 할 수 있는 경우
  Lane2203['pre_lane'].append(1001)
  Lane2203['next_lane'].append(2002)
  MAP['Lane2203']={'Lane2002':Lane2002['s'][-1]}

  Lane2204['pre_lane'].append(2005)
  Lane2204['next_lane'].append(1002)
  MAP['Lane2204']={'Lane1002':Lane1002['s'][-1]}

  Lane2213['pre_lane'].append(2012)
  Lane2213['next_lane'].append(2023)
  MAP['Lane2213']={'Lane2023':Lane2023['s'][-1]}

  Lane2214['pre_lane'].append(2024)
  Lane2214['next_lane'].append(2015)
  MAP['Lane2214']={'Lane2015':Lane2015['s'][-1]}


  Lane2011['pre_lane'].append(2022)
  Lane2011['next_lane'].append(2012)
  MAP['Lane2011']={'Lane2012':Lane2012['s'][-1]}

  Lane2016['pre_lane'].append(2015)
  Lane2016['next_lane'].append(2025)
  MAP['Lane2016']={'Lane2025':Lane2025['s'][-1]}

  Lane2001['pre_lane'].append(2002)
  Lane2001['next_lane'].append(2021)
  MAP['Lane2001']={'Lane2021':Lane2021['s'][-1]}

  Lane2006['pre_lane'].append(2026)
  Lane2006['next_lane'].append(2005)
  MAP['Lane2006']={'Lane2005':Lane2005['s'][-1]}

  Lane2015['pre_lane'].append(2214)
  Lane2015['pre_lane'].append(2103)
  Lane2015['pre_lane'].append(2014)
  Lane2015['next_lane'].append(2016)
  MAP['Lane2015']={'Lane2016':Lane2016['s'][-1]}

  Lane2005['pre_lane'].append(2006)
  Lane2005['next_lane'].append(2204)
  Lane2005['next_lane'].append(2113)
  Lane2005['next_lane'].append(2013)
  MAP['Lane2005']={'Lane2204':Lane2204['s'][-1],'Lane2113':Lane2113['s'][-1],'Lane2013':Lane2013['s'][-1]}

  Lane2002['pre_lane'].append(2203)
  Lane2002['pre_lane'].append(2013)
  Lane2002['pre_lane'].append(2214)
  Lane2002['next_lane'].append(2001)
  MAP['Lane2002']={'Lane2001':Lane2001['s'][-1]}

  Lane2012['pre_lane'].append(2011)
  Lane2012['next_lane'].append(2213)
  Lane2012['next_lane'].append(2104)
  Lane2012['next_lane'].append(2014)
  MAP['Lane2012']={'Lane2213':Lane2213['s'][-1],'Lane2104':Lane2104['s'][-1],'Lane2014':Lane2014['s'][-1]}

  # (1)좌회전 할 수 있는 경우
  Lane2103['pre_lane'].append(1001)
  Lane2103['next_lane'].append(2015)

  MAP['Lane2103']={'Lane2015':Lane2015['s'][-1]}

  Lane2104['pre_lane'].append(2012)
  Lane2104['next_lane'].append(1002)
  MAP['Lane2104']={'Lane1002':Lane1002['s'][-1]}

  Lane2113['pre_lane'].append(2005)
  Lane2113['next_lane'].append(2023)
  MAP['Lane2113']={'Lane2023':Lane2023['s'][-1]}

  Lane2114['pre_lane'].append(2024)
  Lane2114['next_lane'].append(2002)
  MAP['Lane2114']={'Lane2002':Lane2002['s'][-1]}


  # (1)직진 할 수 있는 경우
  Lane2003['pre_lane'].append(1001)
  Lane2003['next_lane'].append(2023)
  MAP['Lane2003']={'Lane2023':Lane2023['s'][-1]}

  Lane2004['pre_lane'].append(2024)
  Lane2004['next_lane'].append(1002)
  MAP['Lane2004']={'Lane1002':Lane1002['s'][-1]}

  Lane2013['pre_lane'].append(2005)
  Lane2013['next_lane'].append(2002)
  MAP['Lane2013']={'Lane2002':Lane2002['s'][-1]}

  Lane2014['pre_lane'].append(2012)
  Lane2014['next_lane'].append(2015)
  MAP['Lane2014']={'Lane2015':Lane2015['s'][-1]}

  # (2) 직선 도로
  Lane2021['pre_lane'].append(2001)
  Lane2021['next_lane'].append(2131)
  Lane2021['next_lane'].append(2031)
  MAP['Lane2021']={'Lane2131':Lane2131['s'][-1],'Lane2031':Lane2031['s'][-1]}

  Lane2022['pre_lane'].append(2031)
  Lane2022['pre_lane'].append(2032)
  Lane2022['next_lane'].append(2011)
  MAP['Lane2022']={'Lane2011':Lane2011['s'][-1]}

  Lane2023['pre_lane'].append(2003)
  Lane2023['next_lane'].append(2232)
  Lane2023['next_lane'].append(2132)
  Lane2023['next_lane'].append(2037)
  MAP['Lane2023']={'Lane2232':Lane2232['s'][-1],'Lane2132':Lane2132['s'][-1],'Lane2037':Lane2037['s'][-1]}


  Lane2024['pre_lane'].append(2233)
  Lane2024['pre_lane'].append(2034)
  Lane2024['pre_lane'].append(2133)
  Lane2024['next_lane'].append(2004)
  Lane2024['next_lane'].append(2114)
  Lane2024['next_lane'].append(2214)
  MAP['Lane2024']={'Lane2004':Lane2004['s'][-1],'Lane2114':Lane2114['s'][-1],'Lane2214':Lane2214['s'][-1]}


  Lane2025['pre_lane'].append(2016)
  Lane2025['next_lane'].append(2234)
  Lane2025['next_lane'].append(2035)
  MAP['Lane2025']={'Lane2234':Lane2234['s'][-1],'Lane2035':Lane2035['s'][-1]}


  Lane2026['pre_lane'].append(2134)
  Lane2026['pre_lane'].append(2036)
  Lane2026['next_lane'].append(2006)
  MAP['Lane2026']={'Lane2006':Lane2006['s'][-1]}

   # (3)우회전 할 경우

  Lane2231['pre_lane'].append(2033)
  Lane2231['next_lane'].append(2022)
  MAP['Lane2231']={'Lane2022':Lane2022['s'][-1]}

  Lane2232['pre_lane'].append(2023)
  Lane2232['next_lane'].append(2033)
  MAP['Lane2232']={'Lane2033':Lane2033['s'][-1]}

  Lane2233['pre_lane'].append(2036)
  Lane2233['next_lane'].append(2024)
  MAP['Lane2233']={'Lane2024':Lane2024['s'][-1]}

  Lane2234['pre_lane'].append(2025)
  Lane2234['next_lane'].append(2036)
  MAP['Lane2234']={'Lane2036':Lane2036['s'][-1]}

  Lane2241['pre_lane'].append(2052)
  Lane2241['next_lane'].append(2043)
  MAP['Lane2241']={'Lane2043':Lane2043['s'][-1]}

  Lane2242['pre_lane'].append(2043)
  Lane2242['next_lane'].append(2053)
  MAP['Lane2242']={'Lane2053':Lane2053['s'][-1]}

  Lane2242['pre_lane'].append(2043)
  Lane2242['next_lane'].append(2053)
  MAP['Lane2242']={'Lane2053':Lane2053['s'][-1]}

  Lane2244['pre_lane'].append(2046)
  Lane2244['next_lane'].append(2055)
  MAP['Lane2244']={'Lane2055':Lane2055['s'][-1]}

  Lane2043['pre_lane'].append(2131)
  Lane2043['pre_lane'].append(2242)
  Lane2043['next_lane'].append(2045)
  Lane2043['next_lane'].append(2133)
  Lane2043['next_lane'].append(2242)
  MAP['Lane2043']={'Lane2045':Lane2045['s'][-1],'Lane2133':Lane2133['s'][-1],'Lane2242':Lane2242['s'][-1]}

  Lane2046['pre_lane'].append(2243)
  Lane2046['pre_lane'].append(2132)
  Lane2046['pre_lane'].append(2045)
  Lane2046['next_lane'].append(2134)
  Lane2046['next_lane'].append(2244)
  MAP['Lane2046']={'Lane2134':Lane2134['s'][-1],'Lane2244':Lane2244['s'][-1]}

  Lane2051['pre_lane'].append(2141)
  Lane2051['pre_lane'].append(2031)
  Lane2051['next_lane'].append(2071)
  MAP['Lane2051']={'Lane2071':Lane2071['s'][-1]}

  Lane2052['pre_lane'].append(2061)
  Lane2052['next_lane'].append(2032)
  Lane2052['next_lane'].append(2241)
  MAP['Lane2052']={'Lane2032':Lane2032['s'][-1],'Lane2241':Lane2241['s'][-1]}


  Lane2053['pre_lane'].append(2037)
  Lane2053['pre_lane'].append(2242)
  Lane2053['pre_lane'].append(2142)
  Lane2053['next_lane'].append(2065)
  Lane2053['next_lane'].append(2261)
  Lane2053['next_lane'].append(2161)
  MAP['Lane2053']={'Lane2065':Lane2065['s'][-1],'Lane2261':Lane2261['s'][-1],'Lane2161':Lane2161['s'][-1]}

  Lane2054['pre_lane'].append(2262)
  Lane2054['pre_lane'].append(2162)
  Lane2054['pre_lane'].append(2066)
  Lane2054['next_lane'].append(2143)
  Lane2054['next_lane'].append(2034)
  Lane2054['next_lane'].append(2243)
  MAP['Lane2054']={'Lane2143':Lane2143['s'][-1],'Lane2034':Lane2034['s'][-1],'Lane2243':Lane2243['s'][-1]}

  Lane2055['pre_lane'].append(2244)
  Lane2055['pre_lane'].append(2035)
  Lane2055['next_lane'].append(2064)
  MAP['Lane2055']={'Lane2064':Lane2064['s'][-1]}

  Lane2056['pre_lane'].append(2074)
  Lane2056['next_lane'].append(2038)
  Lane2056['next_lane'].append(2144)
  MAP['Lane2056']={'Lane2038':Lane2038['s'][-1],'Lane2144':Lane2144['s'][-1]}
  #print(MAP)
  # (3)좌회전 할 경우
  Lane2131['pre_lane'].append(2021)
  Lane2131['next_lane'].append(2043)
  MAP['Lane2131']={'Lane2043':Lane2043['s'][-1]}

  Lane2132['pre_lane'].append(2023)
  Lane2132['next_lane'].append(2046)
  MAP['Lane2132']={'Lane2046':Lane2046['s'][-1]}

  Lane2133['pre_lane'].append(2043)
  Lane2133['next_lane'].append(2024)
  MAP['Lane2133']={'Lane2024':Lane2024['s'][-1]}

  Lane2134['pre_lane'].append(2046)
  Lane2134['next_lane'].append(2026)
  MAP['Lane2134']={'Lane2026':Lane2026['s'][-1]}

  Lane2141['pre_lane'].append(2033)
  Lane2141['next_lane'].append(2051)
  MAP['Lane2141']={'Lane2051':Lane2051['s'][-1]}

  Lane2142['pre_lane'].append(2036)
  Lane2142['next_lane'].append(2053)
  MAP['Lane2142']={'Lane2053':Lane2053['s'][-1]}

  Lane2143['pre_lane'].append(2054)
  Lane2143['next_lane'].append(2033)
  MAP['Lane2143']={'Lane2033':Lane2033['s'][-1]}

  Lane2144['pre_lane'].append(2056)
  Lane2144['next_lane'].append(2036)
  MAP['Lane2144']={'Lane2036':Lane2036['s'][-1]}

  # (3) 직진 할 경우
  Lane2031['pre_lane'].append(2021)
  Lane2031['next_lane'].append(2051)
  MAP['Lane2031']={'Lane2051':Lane2051['s'][-1]}

  Lane2032['pre_lane'].append(2052)
  Lane2032['next_lane'].append(2022)
  MAP['Lane2032']={'Lane2022':Lane2022['s'][-1]}

  Lane2033['pre_lane'].append(2044)
  Lane2033['pre_lane'].append(2143)
  Lane2033['pre_lane'].append(2232)
  Lane2033['next_lane'].append(2231)
  Lane2033['next_lane'].append(2141)
  MAP['Lane2033']={'Lane2231':Lane2231['s'][-1],'Lane2141':Lane2141['s'][-1]}


  Lane2034['pre_lane'].append(2054)
  Lane2034['next_lane'].append(2024)
  MAP['Lane2034']={'Lane2024':Lane2024['s'][-1]}

  Lane2035['pre_lane'].append(2025)
  Lane2035['next_lane'].append(2055)
  MAP['Lane2035']={'Lane2055':Lane2055['s'][-1]}

  Lane2036['pre_lane'].append(2144)
  Lane2036['pre_lane'].append(2234)
  Lane2036['next_lane'].append(2233)
  Lane2036['next_lane'].append(2142)
  Lane2036['next_lane'].append(2044)
  MAP['Lane2036']={'Lane2233':Lane2233['s'][-1],'Lane2142':Lane2142['s'][-1],'Lane2044':Lane2044['s'][-1]}

  Lane2044['pre_lane'].append(2036)
  Lane2044['next_lane'].append(2033)
  MAP['Lane2044']={'Lane2033':Lane2033['s'][-1]}

  Lane2045['pre_lane'].append(2043)
  Lane2045['next_lane'].append(2046)
  MAP['Lane2045']={'Lane2046':Lane2046['s'][-1]}

  Lane2037['pre_lane'].append(2023)
  Lane2037['next_lane'].append(2053)
  MAP['Lane2037']={'Lane2053':Lane2053['s'][-1]}

  Lane2038['pre_lane'].append(2056)
  Lane2038['next_lane'].append(2026)
  MAP['Lane2038']={'Lane2026':Lane2026['s'][-1]}


  # (4) 우회전 할 경우

  Lane2261['pre_lane'].append(2053)
  Lane2261['next_lane'].append(2062)
  MAP['Lane2261']={'Lane2062':Lane2062['s'][-1]}

  Lane2262['pre_lane'].append(2063)
  Lane2262['next_lane'].append(2054)
  MAP['Lane2262']={'Lane2054':Lane2054['s'][-1]}


  Lane2271['pre_lane'].append(2072)
  Lane2271['next_lane'].append(3001)
  MAP['Lane2271']={'Lane3001':Lane3001['s'][-1]}

  Lane2272['pre_lane'].append(3002)
  Lane2272['next_lane'].append(2073)
  MAP['Lane2272']={'Lane2073':Lane2073['s'][-1]}

  Lane2243['pre_lane'].append(2054)
  Lane2243['next_lane'].append(2046)
  MAP['Lane2243']={'Lane2046':Lane2046['s'][-1]}

  # (4) 좌회전 할 경우

  Lane2161['pre_lane'].append(2053)
  Lane2161['next_lane'].append(2073)
  MAP['Lane2161']={'Lane2073':Lane2073['s'][-1]}

  Lane2162['pre_lane'].append(2072)
  Lane2162['next_lane'].append(2054)
  MAP['Lane2162']={'Lane2054':Lane2054['s'][-1]}


  Lane2171['pre_lane'].append(2063)
  Lane2171['next_lane'].append(3001)
  MAP['Lane2171']={'Lane3001':Lane3001['s'][-1]}


  Lane2172['pre_lane'].append(3001)
  Lane2172['next_lane'].append(2062)
  MAP['Lane2172']={'Lane2062':Lane2062['s'][-1]}

  # (4) 직진일 경우

  Lane2051['pre_lane'].append(2141)
  Lane2051['pre_lane'].append(2031)
  Lane2051['next_lane'].append(2071)
  MAP['Lane2051']={'Lane2071':Lane2071['s'][-1]}

  Lane2052['pre_lane'].append(2061)
  Lane2052['next_lane'].append(2032)
  Lane2052['next_lane'].append(2241)
  MAP['Lane2052']={'Lane2032':Lane2032['s'][-1],'Lane2241':Lane2241['s'][-1]}

  Lane2071['pre_lane'].append(2051)
  Lane2071['next_lane'].append(2072)
  MAP['Lane2071']={'Lane2072':Lane2072['s'][-1]}

  Lane2061['pre_lane'].append(2062)
  Lane2061['next_lane'].append(2052)
  MAP['Lane2061']={'Lane2052':Lane2052['s'][-1]}

  Lane2064['pre_lane'].append(2055)
  Lane2064['next_lane'].append(2063)
  MAP['Lane2064']={'Lane2063':Lane2063['s'][-1]}

  Lane2074['pre_lane'].append(2073)
  Lane2074['next_lane'].append(2056)
  MAP['Lane2074']={'Lane2056':Lane2056['s'][-1]}

  Lane2072['pre_lane'].append(2071)
  Lane2072['next_lane'].append(2271)
  Lane2072['next_lane'].append(2162)
  Lane2072['next_lane'].append(2076)
  MAP['Lane2072']={'Lane2271':Lane2271['s'][-1],'Lane2162':Lane2162['s'][-1],'Lane2076':Lane2076['s'][-1]}

  Lane2062['pre_lane'].append(2261)
  Lane2062['pre_lane'].append(2075)
  Lane2062['pre_lane'].append(2172)
  Lane2062['next_lane'].append(2061)
  MAP['Lane2062']={'Lane2061':Lane2061['s'][-1]}

  Lane2073['pre_lane'].append(2076)
  Lane2073['pre_lane'].append(2161)
  Lane2073['pre_lane'].append(2272)
  Lane2073['next_lane'].append(2074)
  MAP['Lane2073']={'Lane2074':Lane2074['s'][-1]}

  Lane2063['pre_lane'].append(2064)
  Lane2063['next_lane'].append(2171)
  Lane2063['next_lane'].append(2075)
  Lane2063['next_lane'].append(2262)
  MAP['Lane2063']={'Lane2171':Lane2171['s'][-1],'Lane2075':Lane2075['s'][-1],'Lane2262':Lane2262['s'][-1]}

  Lane2065['pre_lane'].append(2053)
  Lane2065['next_lane'].append(3001)
  MAP['Lane2065']={'Lane3001':Lane3001['s'][-1]}

  Lane2066['pre_lane'].append(3002)
  Lane2066['next_lane'].append(2054)
  MAP['Lane2066']={'Lane2054':Lane2054['s'][-1]}

  Lane2076['pre_lane'].append(2072)
  Lane2076['next_lane'].append(2073)
  MAP['Lane2076']={'Lane2073':Lane2073['s'][-1]}

  Lane2075['pre_lane'].append(2063)
  Lane2075['next_lane'].append(2062)
  MAP['Lane2075']={'Lane2062':Lane2062['s'][-1]}


  for i in final_data_cand  :
    #print(i['id'], i['next_lane'])
    for j in i['next_lane']:
        x,y,yaw,k,s=combine_two_lane(i, globals()['Lane{}'.format(j)])
        '''
        if y==999 :
          print('type 2')
          plt.plot(i['x']+globals()['Lane{}'.format(j)]['x'],i['y']+globals()['Lane{}'.format(j)]['y'] )
          plt.scatter(i['x']+globals()['Lane{}'.format(j)]['x'],i['y']+globals()['Lane{}'.format(j)]['y'], marker='.')
          plt.title(i['id']+' '+globals()['Lane{}'.format(j)]['id'])
          plt.show()
        elif x==999 :
          print('type 1')
          plt.plot(i['x']+globals()['Lane{}'.format(j)]['x'],i['y']+globals()['Lane{}'.format(j)]['y'] )
          plt.scatter(i['x']+globals()['Lane{}'.format(j)]['x'],i['y']+globals()['Lane{}'.format(j)]['y'], marker='.')
          plt.title(i['id']+' '+globals()['Lane{}'.format(j)]['id'])
          plt.show()
        '''
        
  while 1:
    departure = nearest_dpt_lane(x1, y1)
    departure = ('Lane{}'.format(departure))
    destination = nearest_dst_lane()
    destination = ('Lane{}'.format(destination))
    if departure=='Lane3001' or departure=='Lane3002':
      print("출발지를 다시 입력해주세요.\n")
    else:
      break

  print ("-----------[", departure, "->", destination,"]----------")

  #다이제스트라 알고리즘
  
  sdistance=99999
  sid='Lane0417'
  list2=["","",""]
  list3=["","",""]
  path={}
  if departure=='Lane1001':
    list1=['Lane2003','Lane2103','Lane2203']
    x=0
    while True:
      if(x==3):
        break
      de=list1[x]
      print(de)
     
      for place in MAP.keys():
          path[place]={'shortestDist':0, 'route':[], 'visited':0}
                 
      visitPlace(de,path,MAP)
      
      while 1 :
          minDist = max(path.values(), key=lambda x:x['shortestDist'])['shortestDist']
          toVisit = ''
          for name, search in path.items():
              if 0 < search['shortestDist'] <= minDist and not search['visited']:
                  minDist = search['shortestDist']
                  toVisit = name
          if toVisit == '':
              break
          visitPlace(toVisit,path,MAP)
      x=x+1
      if sdistance>path[destination]['shortestDist']:
        sdistance=path[destination]['shortestDist']
        sid=de
    departure=sid
  for place in MAP.keys():
      path[place]={'shortestDist':0, 'route':[], 'visited':0}
             
  visitPlace(departure,path,MAP)
 
  while 1 :
      minDist = max(path.values(), key=lambda x:x['shortestDist'])['shortestDist']
      toVisit = ''
      for name, search in path.items():
          if 0 < search['shortestDist'] <= minDist and not search['visited']:
              minDist = search['shortestDist']
              toVisit = name
      if toVisit == '':
          break
      visitPlace(toVisit,path,MAP)


      print ("["+toVisit+"]")   
      print ("Dist :", minDist+globals()['Lane{}'.format('1001')]['s'][-1])
  #print(path)
  if sid is not'Lane0417':
    print ("\n", "[Lane1001->", destination,"]")
    print ("Route : ", path[destination]['route'])
    print ("ShortestDistance : ", path[destination]['shortestDist']+globals()['Lane{}'.format('1001')]['s'][-1])
  else :
    print ("\n", "[",departure,"->", destination,"]")
    print ("Route : ", path[destination]['route'])
    print ("ShortestDistance : ", path[destination]['shortestDist'])

  Lane9999 = {'id': 9999,'x':[], 'y':[], 'yaw':[], 'k':[],'s':[], 'pre_lane': [], 'next_lane': []}
  if sid is not'Lane0417':
    Lane9999=final(departure,path,destination,globals()['Lane{}'.format('1001')],1)
  else:
    Lane9999=final(departure,path,destination,globals()['Lane{}'.format('1001')],0)




  return Lane9999['x'],Lane9999['y'],Lane9999['yaw'],Lane9999['k'],Lane9999['s']

def make_txt(x1, y1): 
  
  cx=[]
  cy=[]
  cyaw=[]
  ck=[]
  cs=[]

  cx,cy,cyaw,ck,cs=make_line(x1,y1)
  
  with open("C:/Users/sun84/Desktop/ygs.txt",mode="w") as file:    #만드려고하는 파일명 

    j=0
    i=0

    while True :

      file.write(str(cx[i])+"\t"+str(cy[i])+"\t"+str(cyaw[i])+"\t"+str(ck[i])+"\t"+str(cs[i])+"\n")
      if cx[-1]==cx[i]:
        break
      i=i+1
    file.close()

if __name__ == "__main__":
  make_txt()
  #make_line()

'''
plt.plot(Lane2055['x'],Lane2055['y'])
plt.scatter(Lane2055['x'],Lane2055['y'],marker=',')
plt.show()
'''
# print(files)
# print(len(final_data_cand))


###### make txt file on dictionary format ###### i'm not sure if i'm gonna use this.. 

# final_data = open('final_data.txt','w')

# for i in final_data_cand:
#    i = str(i)
#    final_data.write(i + '\n' + '\n'+ '\n'+ '\n'+ '\n'+ '\n'+ '\n')
   
# final_data.close()