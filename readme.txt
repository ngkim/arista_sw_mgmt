
<개요>
- Arista switch의 eAPI를 이용하여 Arista 7050 스위치를 구성 및 모니터링

<작업기록> 

- 2014.09.19

* utils.py에 list_str_to_int 함수 추가 
	- switch 설정 파일에 인터페이스 목록을 입력할 때 1-4,7,9와 같이 간편하게 입력할 수 있도록 하기 위함
	- 사용법은 test/test-config-parser.py의 test_get_int에서 확인할 수 있음 
	

* failover
	UTM VM 다운이나 Cloud C-node 다운 시에 Baremetal UTM으로 절체해주는 기능
	원래는 Trunk port에서 UTM용 GREEN이나 ORANGE VLAN을 제거해주는 형태로 동작해야 하나, 여기에서는 스위치의 포트를 shutdown시키는 형태로만 동작
