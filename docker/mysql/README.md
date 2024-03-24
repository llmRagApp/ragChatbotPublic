
### 빅데이터센터에서 받은 개발서버에 devuser로 docker 및 docker-compose 설치

#### 추가로 mysql을 docker로 구동
---

  ```shell
# Docker 설치
# root로 설치, 
# 만일 devuser로 설치할경우 앞에 devuser에게 sudo 권한부여해야합니다.
# mysql : version 5.7
# MYSQL_ROOT_PASSWORD: llmrag
# MYSQL_DATABASE: wc
# MYSQL_USER: wc
# MYSQL_PASSWORD: wc1!#
# mysql 데이터 경로 : /home/ai/src/mysql57/data
  ```

#### root 유져로 로그인

  ```shell
(base) [root@localhost ~]# su -
  ```

#### docker 설치를 위해 yum 업데이트

  ```shell
(base) [root@localhost ~]# sudo yum -y update
  ```

#### yum-utils 패키지(yum-config-manager 유틸리티 제공)를 설치하고 저장소를 설정

  ```shell
(base) [root@localhost ~]# sudo yum install -y yum-utils
(base) [root@localhost ~]# sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
  ```

#### Docker 설치

  ```shell
(base) [root@localhost ~]# sudo yum install docker-ce docker-ce-cli containerd.io -y
  ```

#### 도커 시작

  ```shell
(base) [root@localhost ~]# sudo systemctl start docker
  ```

#### 도커 상태확인

  ```shell
(base) [root@localhost ~]# sudo systemctl status docker
  ```

#### 부팅시 도커 시작하도록 세팅

  ```shell
(base) [root@localhost ~]# sudo systemctl enable docker
(base) [root@localhost ~]# docker --version
Docker version 26.0.0, build 2ae903e
  ```
<br> # root 권한이 아닌 일반 사용자로 Docker 관리하기
<br> # Docker 데몬은 항상 root 사용자로 실행됨
<br> # docker 명령어 사용 시 sudo를 사용하지 않으려면 docker 그룹을 생성하고 사용자 추가 필요

#### docker 그룹 생성 (Docker 설치 시 자동으로 생성되어있을 수 있음)

  ```shell
(base) [root@localhost ~]# sudo groupadd docker
  ```

#### docker 그룹에 사용자 추가

  ```shell
(base) [root@localhost ~]# sudo usermod -aG docker $USER
  ```

#### 그룹 변경 사항 활성화

  ```shell
(base) [root@localhost ~]# newgrp docker
  ```

#### systemctl 명령어를 사용하여 부팅 시 docker가 자동으로 실행되도록 설정 가능

  ```shell
(base) [root@localhost ~]# sudo systemctl enable docker.service
(base) [root@localhost ~]# sudo systemctl enable containerd.service
  ```

#### 자동 실행 설정을 해제하려면 disable 명령어 사용

  ```shell
(base) [root@localhost ~]# sudo systemctl disable docker.service
(base) [root@localhost ~]# sudo systemctl disable containerd.service
  ```

# docker compose 설치
---
#### 다운로드 받을 디렉토리 생성

  ```shell
$ mkdir temp
$ cd temp
  ```
#### docker-compose 다운로드

  ```shell
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

#### docker-compose 실행권한설정

  ```shell
[devuser@localhost temp]$ sudo chmod +x /usr/local/bin/docker-compose
[devuser@localhost temp]$ docker-compose --version
Docker Compose version v2.24.6
[devuser@localhost temp]$
  ```

# docker compose로 mysql 5.6 설치
---

#### directory에 mysql 폴더 생성

  ```shell
(base) [root@localhost ~]# cd /home/ai/src
(base) [root@localhost src]# mkdir mysql57
  ```

#### docker-compose 파일이있는 디렉토리로 이동

  ```shell
(base) [root@localhost src]# cd /home/ai/src/ragChatbotPublic/docker/mysql
  ```

#### docker-compose로 구동하기

  ```shell
(base) [root@localhost mysql]# docker-compose up -d
(base) [root@localhost mysql]# docker ps
CONTAINER ID   IMAGE       COMMAND                   CREATED              STATUS          PORTS                                                  NAMES
72727a9fba7e   mysql:5.7   "docker-entrypoint.s…"   About a minute ago   Up 29 seconds   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysql57
(base) [root@localhost mysql]#
  ```


#### docker-compose 명령어

  ```shell
# docker-compose로 mysql 도커 구동
(base) [root@localhost mysql]# docker-compose up -d  
# docker-compose로 구동한 docker를 삭제
(base) [root@localhost mysql]# docker-compose down    
# 현재 구동중인 docker를 중지
(base) [root@localhost mysql]# docker-compose stop 
# 중지한 docker를 재시작
(base) [root@localhost mysql]# docker-compose start   
  ```

#### 도커로 들어가기
  ```shell
(base) [root@localhost mysql]# docker exec -it mysql57 bash
bash-4.2#
  ```

#### 도커의 mysql57에 연결하기
  ```shell
bash-4.2# mysql -h 127.0.0.1 -u wc -p
Enter password: wc1!#
  ```

#### Host 서버에서 docker의 mysql에 연결
  ```shell
(base) [root@localhost mysql]# mysql -h 127.0.0.1 -u wc -p
Enter password: wc1!#
  ```



