#!/bin/env python
#-*- coding:utf-8 -*-
#------------------------------------------------------------------------------
#
#   システム名      :   医療情報システム
#
#   サブシステム名  :   院内メールシステム
#
#   プログラム名    :   pop3mail
#
#   モジュール名    :   pop3mail.py
#
#   処理内容        :   POP3サーバからメール受信
#
#   注意事項        :   CentOS6では #!/bin/env python
#                       CentOS7では #!/usr/bin/env python
#
#   作成日(担当者)  :   2018/03/16(山脇)
#   修正日(担当者)  :
#
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#   ライブライのインポート
#------------------------------------------------------------------------------
# ライブラリのインポート
import sys
import poplib
import email
import email.header
import email.parser
import datetime
import os
import socket
import fcntl
import getpass
import getopt
import shutil
import time
import re

#------------------------------------------------------------------------------
#   グローバル変数
#------------------------------------------------------------------------------
# POP3ホスト名
pop3_hostnm = ''
# POP3ユーザ名
pop3_userid = ''
# POP3パスワード
pop3_passwd = ''

# vmaildir
vmail_dir = '/var/spool/vmail/almeida.oita.med.or.jp/'

# Maildir
mail_dir = 'Maildir/'

# デバック
debug = False


#------------------------------------------------------------------------------
#
#   クラス名    :   pop3mail
#   内　　容    :   POP3メール解析
#
#------------------------------------------------------------------------------
class pop3mail(object):
    #--------------------------------------------------------------------------
    #
    #   メソッド名  :   コンストラクタ
    #
    #--------------------------------------------------------------------------
    def __init__(self, pop3, which):
        #----------------------------------------------------------------------
        #   メールの解析
        #----------------------------------------------------------------------
        # 初期化
        mail_str = ""
        mail_size = 0

        # 開始時間(計測開始)
        start = time.time()

        # FeedParserインスタンスの作成
        fp = email.parser.FeedParser()

        # 1行ずつ取得
        for mail_decode in pop3.retr(which)[1]:
            # メールのデコード
            # ※デコードされているので不要
            #*////mail_decode = mail_bytes.decode()
            # FeedParserへのデータ供給
            fp.feed(mail_decode)
            fp.feed('\n')

            # サイズの計算
            mail_size = mail_size + len(mail_decode) + 1
            # メッセージのデコードと結合
            mail_str = mail_str + mail_decode + '\r\n'

            # 経過時間
            elapsed_time = time.time() - start

            # 接続維持判定
            if elapsed_time > 60:
                # 接続維持(60秒ごとに接続維持)
                pop3.noop()
                # 開始時間(再計測)
                start = time.time()

        # データ解析
        mail_msg = fp.close()
        #*////# メッセージのパース
        #*////mail_msg = email.message_from_string(mail_str)

        # Receivedの取得
        mail_received = mail_msg.get('Received')
        # Dateの情報
        mail_date = mail_msg.get('Date')
        # NoneTypeの判定
        if mail_received != None:
            # 受信日時の取得
            mail_datetime = mail_received.split(';')[1].split('(')[0].strip()

        elif mail_date != None:
            # 送信日時の取得
            mail_datetime = mail_date.split('(')[0]

        else:
            # システム日付の取得
            mail_datetime = datetime.datetime.now().strftime('%a, %d %b %Y %X +0900')

        # 文字列から日付に変換
        # 例) Tue,  4 Nov 2014 10:55:12 +0900 → 2014-11-04 10:55:12
        #*////self.date = datetime.datetime.strptime(mail_datetime, '%a, %d %b %Y %X %z')
        # タイムゾーンの取得
        mail_timezone = re.search(' \+[0-9]{4}', mail_datetime)
        if mail_timezone != None:
            # タイムゾーンの除去
            mail_datetime = mail_datetime.replace(mail_timezone.group(), '')
            # 日付に変換
            self.date = datetime.datetime.strptime(mail_datetime, '%a, %d %b %Y %X')
            # タイムゾーンの加算
            if mail_timezone.group() == ' -1200':
                # ベーカー島、ハウランド島
                self.date = self.date + datetime.timedelta(hours=21)

            elif mail_timezone.group() == ' -1100':
                # アメリカ領サモア、ニウエ
                self.date = self.date + datetime.timedelta(hours=20)

            elif mail_timezone.group() == ' -1000':
                # ハワイ、アリューシャン列島西部
                self.date = self.date + datetime.timedelta(hours=19)

            elif mail_timezone.group() == ' -0930':
                # フランス領ポリネシア（マルキーズ諸島）
                self.date = self.date + datetime.timedelta(hours=18)
                self.date = self.date + datetime.timedelta(minutes=30)

            elif mail_timezone.group() == ' -0900':
                # アラスカ
                self.date = self.date + datetime.timedelta(hours=18)

            elif mail_timezone.group() == ' -0800':
                # アメリカ・カナダ・メキシコ（太平洋時間）
                self.date = self.date + datetime.timedelta(hours=17)

            elif mail_timezone.group() == ' -0700':
                # アメリカ・カナダ・メキシコ（山岳部時間）
                self.date = self.date + datetime.timedelta(hours=16)

            elif mail_timezone.group() == ' -0600':
                # アメリカ・カナダ・メキシコ（中部時間）、中央アメリカ
                self.date = self.date + datetime.timedelta(hours=15)

            elif mail_timezone.group() == ' -0500':
                # アメリカ・カナダ（東部時間）、キューバ、ペルー
                self.date = self.date + datetime.timedelta(hours=14)

            elif mail_timezone.group() == ' -0400':
                # カナダ（大西洋時間）、ベネズエラ、ブラジル（アマゾン時間）、チリ
                self.date = self.date + datetime.timedelta(hours=13)

            elif mail_timezone.group() == ' -0330':
                # カナダ（ニューファンドランド）
                self.date = self.date + datetime.timedelta(hours=12)
                self.date = self.date + datetime.timedelta(minutes=30)

            elif mail_timezone.group() == ' -0300':
                # ブラジル（ブラジル時間）、アルゼンチン、グリーンランド
                self.date = self.date + datetime.timedelta(hours=12)

            elif mail_timezone.group() == ' -0200':
                # ブラジル（フェルナンド・デ・ノローニャ島）
                self.date = self.date + datetime.timedelta(hours=11)

            elif mail_timezone.group() == ' -0100':
                # アゾレス諸島、カーボベルデ
                self.date = self.date + datetime.timedelta(hours=10)

            elif mail_timezone.group() == ' +0000':
                # イギリス、アイルランド、ポルトガル、アイスランド、アフリカ西部
                self.date = self.date + datetime.timedelta(hours=9)

            elif mail_timezone.group() == ' +0100':
                # 中央ヨーロッパ時間、西アフリカ時間
                self.date = self.date + datetime.timedelta(hours=8)

            elif mail_timezone.group() == ' +0200':
                # 東ヨーロッパ時間、中央アフリカ時間、南アフリカ
                self.date = self.date + datetime.timedelta(hours=7)

            elif mail_timezone.group() == ' +0300':
                # ロシア（モスクワ）、ベラルーシ、サウジアラビア、東アフリカ時間
                self.date = self.date + datetime.timedelta(hours=6)

            elif mail_timezone.group() == ' +0330':
                # イラン
                self.date = self.date + datetime.timedelta(hours=5)
                self.date = self.date + datetime.timedelta(minutes=30)

            elif mail_timezone.group() == ' +0400':
                # ロシア（サマラ）、アゼルバイジャン、グルジア、アラブ首長国連邦、モーリシャス
                self.date = self.date + datetime.timedelta(hours=5)

            elif mail_timezone.group() == ' +0430':
                # アフガニスタン
                self.date = self.date + datetime.timedelta(hours=4)
                self.date = self.date + datetime.timedelta(minutes=30)

            elif mail_timezone.group() == ' +0500':
                # ロシア（エカテリンブルグ）、パキスタン
                self.date = self.date + datetime.timedelta(hours=4)

            elif mail_timezone.group() == ' +0530':
                # インド
                self.date = self.date + datetime.timedelta(hours=3)
                self.date = self.date + datetime.timedelta(minutes=30)

            elif mail_timezone.group() == ' +0545':
                # ネパール
                self.date = self.date + datetime.timedelta(hours=3)
                self.date = self.date + datetime.timedelta(minutes=15)

            elif mail_timezone.group() == ' +0600':
                # ロシア（オムスク）、カザフスタン、バングラディシュ
                self.date = self.date + datetime.timedelta(hours=3)

            elif mail_timezone.group() == ' +0630':
                # ミャンマー、ココス諸島
                self.date = self.date + datetime.timedelta(hours=2)
                self.date = self.date + datetime.timedelta(minutes=30)

            elif mail_timezone.group() == ' +0700':
                # ロシア（クラスノヤルスク）、タイ、ベトナム、インドネシア西部時間
                self.date = self.date + datetime.timedelta(hours=2)

            elif mail_timezone.group() == ' +0800':
                # ロシア（イルクーツク）、中国、モンゴル、マレーシア、オーストラリア西部時間
                self.date = self.date + datetime.timedelta(hours=1)

            elif mail_timezone.group() == ' +0830':
                # 北朝鮮
                self.date = self.date + datetime.timedelta(minutes=30)

            elif mail_timezone.group() == ' +0845':
                # オーストラリア（ユークラ）
                self.date = self.date + datetime.timedelta(minutes=15)

            elif mail_timezone.group() == ' +0900':
                # ロシア（ヤクーツク）、韓国、日本、パラオ
                self.date = self.date + datetime.timedelta(hours=0)

            elif mail_timezone.group() == ' +0930':
                # オーストラリア中部時間
                self.date = self.date + datetime.timedelta(minutes=-30)

            elif mail_timezone.group() == ' +1000':
                # ロシア（ウラジオストク）、グアム、オーストラリア東部時間
                self.date = self.date + datetime.timedelta(hours=-1)

            elif mail_timezone.group() == ' +1030':
                # オーストラリア（ロード・ハウ島）
                self.date = self.date + datetime.timedelta(hours=-1)
                self.date = self.date + datetime.timedelta(minutes=-30)

            elif mail_timezone.group() == ' +1100':
                # ロシア（マガダン）、ソロモン諸島、ニューカレドニア
                self.date = self.date + datetime.timedelta(hours=-2)

            elif mail_timezone.group() == ' +1200':
                # ロシア（カムチャッカ）、ニュージーランド、フィジー、キリバス（ギルバート諸島）
                self.date = self.date + datetime.timedelta(hours=-3)

            elif mail_timezone.group() == ' +1245':
                # ニュージーランド（チャタム島）
                self.date = self.date + datetime.timedelta(hours=-3)
                self.date = self.date + datetime.timedelta(minutes=-45)

            elif mail_timezone.group() == ' +1300':
                # トンガ、キリバス（フェニックス諸島）、サモア、トケラウ
                self.date = self.date + datetime.timedelta(hours=-4)

            elif mail_timezone.group() == ' +1400':
                # キリバス（ライン諸島）
                self.date = self.date + datetime.timedelta(hours=-5)

        else:
            # 日付に変換
            self.date = datetime.datetime.strptime(mail_datetime, '%a, %d %b %Y %X')

        # UNIX timeの取得
        # 例) 2014-11-04 10:55:12 → 1415066112
        timestamp = int(time.mktime(self.date.timetuple()))
        self.timestamp = str(timestamp)
        # サイズの取得(CR)
        self.size = mail_size
        # サイズの取得(CR+LF)
        self.wsize = len(mail_str)
        # メール全文
        self.message = mail_str

        # Fromの取得
        self.mailfrom = self.get_header(mail_msg, 'From')
        # Subjectの取得
        self.subject = self.get_header(mail_msg, 'Subject')
        # 本文の取得
        self.content = self.get_content(mail_msg)

    #--------------------------------------------------------------------------
    #
    #   メソッド名  :   get_header
    #   内　　　容  :   ヘッダの取得
    #
    #--------------------------------------------------------------------------
    def get_header(self, msg, name):
        # 初期化
        mail_header = ''

        #----------------------------------------------------------------------
        #   ヘッダの取得とデコード
        #----------------------------------------------------------------------
        try:
            # 存在判定
            if msg[name]:
                # ヘッダの取得
                mail_get = msg.get(name)
                # ヘッダのデコード
                mail_enc = email.header.decode_header(mail_get)[0]
                # バイト文字の判定
                if type(mail_enc[0]) is bytes:
                    # 文字セットの取得
                    mail_charset = mail_enc[1]
                    # 文字セットの判定
                    if mail_charset:
                        # 文字セットでのデコード
                        mail_header = mail_enc[0].decode(mail_charset)

                    else:
                        # 文字列へのデコード
                        mail_header = mail_enc[0].decode()

                else:
                    # 文字列
                    mail_header = mail_enc[0]

        except Exception as e:
            # エラー表示
            print('{0}'.format(e))

        # ヘッダを返す
        return(mail_header)

    #--------------------------------------------------------------------------
    #
    #   メソッド名  :   get_content
    #   内　　　容  :   本文の取得
    #
    #--------------------------------------------------------------------------
    def get_content(self, msg):
        # 初期化
        mail_content = ''

        # 文字セットの取得
        mail_charset = msg.get_content_charset()
        # ペイロードの取得
        mail_payload = msg.get_payload(decode=True)

        #----------------------------------------------------------------------
        #   本文の取得とデコード
        #----------------------------------------------------------------------
        try:
            # ペイロードの判定
            if mail_payload:
                # 文字セットの判定
                if mail_charset:
                    # 文字セットでのデコード
                    mail_content = mail_payload.decode(mail_charset)

                else:
                    # 文字列へのデコード
                    mail_content = mail_payload.decode()

            # 本文を返す
            return(mail_content)

        except Exception as e:
            # 生データを返す
            return(mail_payload)

#------------------------------------------------------------------------------
#
#   関数名  :   connect_pop3
#   内　容  :   POP3サーバ接続
#
#------------------------------------------------------------------------------
def connect_pop3(pop3, host):
    #--------------------------------------------------------------------------
    #   POP3サーバへの接続
    #--------------------------------------------------------------------------
    try:
        # POP3サーバ接続
        pop3 = poplib.POP3(host)

    except Exception as e:
        # エラー表示
        print('{0}'.format(e))
        # 異常終了
        return(True)

    # 正常終了
    return(False)

#------------------------------------------------------------------------------
#
#   関数名  :   login_pop3
#   内　容  :   POP3サーバ認証
#
#------------------------------------------------------------------------------
def login_pop3(pop3, userid, passwd):
    #--------------------------------------------------------------------------
    #   POP3サーバへのログイン
    #--------------------------------------------------------------------------
    try:
        # POP3認証
        pop3.user(userid)
        pop3.pass_(passwd)

    except Exception as e:
        # エラー表示
        print('{0}'.format(e))
        # 異常終了
        return(True)

    # 正常終了
    return(False)

#------------------------------------------------------------------------------
#
#   関数名  :   get_uidlist
#   内　容  :   dovecot-uidlist取得
#
#------------------------------------------------------------------------------
def get_uidlist(utop, ulist, fpath, flock):
    """
    ---------------------------------------------------------------------------
    (詳細内容)
    ---------------------------------------------------------------------------
     1) 1行目は制御レコード
    ---------------------------------------------------------------------------
     3 V1415066116 N3988 Ge2ac2e31182caa5a684e00007668e450
     | ||          ||    |
     | ||          ||    +--メールボックのグローバルUID(128bit)
     | ||          |+-------次のメッセージUID
     | ||          +--------"N"固定
     | |+-------------------IMAP UIDVALIDITY
     | +--------------------"V"固定
     +----------------------フォーマットバージョン

    ---------------------------------------------------------------------------
     2) 2行目以降はメール一覧(以下の2パターンが存在)
    ---------------------------------------------------------------------------
     2025 S3614 W3675 :1521080790.02025.mail.domain.jp
     |    |            |
     |    |            +--ファイル名
     |    +---------------メールサイズ
     |                     S:ファイルサイズ
     |                     W:RFC822サイズ(CR+LF改行)
     +--------------------メッセージUID

     2026 :1521101888.M494328P20077.mail.domain.jp,S=6150,W=6289
     |    |
     |    +---------------ファイル名
     +--------------------メッセージUID

    ---------------------------------------------------------------------------
     3) ファイル名はユニークになるように作成(特に制限は無いが以下が標準)
    ---------------------------------------------------------------------------
     1521101888.M494328P20077.mail.domain.jp,S=6150,W=6289
     |          |      |      |              |
     |          |      |      |              +-メールサイズ
     |          |      |      |                 S:ファイルサイズ
     |          |      |      |                 W:RFC822サイズ(CR+LF改行)
     |          |      |      +----------------ホスト名
     |          |      +-----------------------"P"+プロセスID
     |          +------------------------------"M"+ファイルのマイクロ秒
     +-----------------------------------------メール受信日時(UNIX time)

     1520981729.Vfd04I1c9a44M897204.mai.domain
     |          |    |      |       |
     |          |    |      |       +----------ホスト名
     |          |    |      +------------------"M"+ファイルのマイクロ秒
     |          |    +-------------------------"I"+i-node番号
     |          +------------------------------"V"+デバイス番号
     +-----------------------------------------メール受信日時(UNIX time)

    ---------------------------------------------------------------------------
     4) ファイルロックの制御
    ---------------------------------------------------------------------------
     dovecot-uidlistのファイルロック制御はdovecot-uidlist.lockを作成するこ
     とで行う。
    ---------------------------------------------------------------------------
    """
    #--------------------------------------------------------------------------
    #   dovecot-uidlistの取得
    #--------------------------------------------------------------------------
    try:
        # ファイルオープン
        fn = open(fpath, 'r')

        """
        dovecot-uidlistからUIDLを取得して辞書に格納
        """
        # UID-Validity
        uidv = ''
        # 1行ずつ読み込む
        for line in fn:
            # スペース分割
            array = line.split()

            # UIDVの取得
            if uidv == '':
                # バージョン判定
                if array[0] != '3':
                    # エラー終了
                    raise Exception('Format Version Error')

                # UIDVALIDITY判定
                if array[1][0:1] != 'V':
                    # エラー終了
                    raise Exception('UIDVALIDITY Error')

                # UIDVALIDITY取得
                uidv = '{0:0>8}'.format(hex(int(array[1][1:], 10))[2:])
                if uidv == "":
                    # エラー終了
                    raise Exception('UIDVALIDITY Error')

                # リストに格納
                for value in array:
                    # リストに追加
                    utop.append(value)

            else:
                # UIDの取得
                xuid = '{0:0>8}'.format(hex(int(array[0], 10))[2:])

                # 辞書に格納
                ulist[xuid + uidv] = line.replace('\r', '').replace('\n', '')

    except Exception as e:
        # エラー表示
        print('{0}'.format(e))
        # 異常終了
        return(True)

    finally:
        # ファイルクローズ
        fn.close()

    # 正常終了
    return(False)

#------------------------------------------------------------------------------
#
#   関数名  :   usage
#   内　容  :   使用方法
#
#------------------------------------------------------------------------------
def usage():
    #--------------------------------------------------------------------------
    #   使用方法の表示
    #--------------------------------------------------------------------------
    print('Usage: -H hostnm [-u userid] [-p password] [-d]')
    print('Options and arguments (and corresponding environment variables):')
    print('-H     : pop3 host name')
    print('-u     : pop3 user name')
    print('-p     : pop3 password')
    print('-d     : debug mode')

#------------------------------------------------------------------------------
#
#   関数名  :   main
#   内　容  :   主処理
#
#------------------------------------------------------------------------------
def main():
    # 初期化
    global pop3_hostnm
    global pop3_userid
    global pop3_passwd
    global debug

    #--------------------------------------------------------------------------
    #   オプションの取得と解析
    #--------------------------------------------------------------------------
    try:
        # オプションの取得
        opts, args = getopt.getopt(sys.argv[1:],
                                   'dH:u:p:',
                                   ['host=', 'user=', 'pass='])

        # オプションの解析
        for opt, arg in opts:
            # オプションの判定
            if opt == '-d':
                # デバック
                debug = True

            elif opt in ('-H', '--host'):
                # ホスト名
                pop3_hostnm = arg

            elif opt in ('-u', '--user'):
                # ユーザ名
                pop3_userid = arg

            elif opt in ('-p', '--pass'):
                # パスワード
                pop3_passwd = arg

    except getopt.GetoptError as e:
        # エラー表示
        print('{0}'.format(e))
        # 使用方法
        usage()
        # 異常終了
        return(True)

    #--------------------------------------------------------------------------
    #   オプションの判定
    #--------------------------------------------------------------------------
    # ホスト名
    if pop3_hostnm == '':
        # 使用方法
        usage()
        # 異常終了
        return(True)

    # ユーザ名
    if pop3_userid == '':
        # ユーザ名
        pop3_userid = getpass.getuser()

    # パスワード
    if pop3_passwd == '':
        # パスワード
        pop3_passwd = pop3_userid

    #--------------------------------------------------------------------------
    #   初期処理
    #--------------------------------------------------------------------------
    # User Home
    if vmail_dir == '':
        home_dir = '/home/' + pop3_userid + '/'
    else:
        home_dir = vmail_dir + pop3_userid + '/'
    # Maildir存在判定
    if not os.path.isdir( home_dir + mail_dir ):
        # 異常終了
        return(True)

    # dovecot-uidlist
    # ※dovecotのuidlist
    uidlist_path = home_dir + mail_dir + 'dovecot-uidlist'
    uidlist_lock = home_dir + mail_dir + 'dovecot-uidlist.lock'

    # dovecot-uidlist.UIDVALIDITY
    # ※pop3のuidlist
    uidlist_local = ''

    # new
    new_dir = home_dir + mail_dir + 'new/'
    # tmp
    tmp_dir = home_dir + mail_dir + 'tmp/'

    #--------------------------------------------------------------------------
    #   POP3サーバへの接続
    #--------------------------------------------------------------------------
    try:
        # POP3サーバ接続
        pop3 = poplib.POP3(pop3_hostnm)

    except Exception as e:
        # エラー表示
        print('{0}'.format(e))
        # 異常終了
        return(True)

    #--------------------------------------------------------------------------
    #   メール取得処理
    #--------------------------------------------------------------------------
    try:
        #----------------------------------------------------------------------
        #   POP3サーバの認証
        #----------------------------------------------------------------------
        # POP3サーバの認証
        if login_pop3(pop3, pop3_userid, pop3_passwd):
            # 異常終了
            return(True)

        #----------------------------------------------------------------------
        #   dovecot-uidlistの取得
        #----------------------------------------------------------------------
        # 初期化
        uidtop = []
        uidlist = {}
        # dovecot-uidlist取得
        if get_uidlist(uidtop, uidlist, uidlist_path, uidlist_lock):
            # 異常終了
            sys.exit()

        # UIDVALIDITYの取得
        uidvalidity = '{0:0>8}'.format(hex(int(uidtop[1][1:], 10))[2:])
        uidlist_local = uidlist_path + '.' + uidvalidity

        #----------------------------------------------------------------------
        #   uidlistの取得
        #----------------------------------------------------------------------
        # ファイル存在チェック
        if not os.path.isfile(uidlist_local):
            #------------------------------------------------------------------
            #   dovecot-uidlistの取得
            #------------------------------------------------------------------
            try:
                # ファイルオープン
                fn = open(uidlist_local, 'a')
                # 制御レコードの書き込み
                for idx1 in range(0, len(uidtop)):
                    # 初期判定
                    if idx1 != 0:
                        # 区切り文字
                        fn.write(' ')

                    # 書き込み
                    fn.write(uidtop[idx1])

                # 改行出力
                fn.write('\n')

                # dovecot-uidlistの書き込み
                for key, value in uidlist.items():
                    # 移行データの判定
                    array = value.split(':')
                    array = array[1].split('.')
                    if array[1][0:1] == 'M':
                        # 続行
                        continue

                    # 書き込み
                    fn.write(value + '\n')

            except Exception as e:
                # エラー表示
                print('{0}'.format(e))
                # 異常終了
                return(True)

            finally:
                # ファイルクローズ
                fn.close()

        #----------------------------------------------------------------------
        #   dovecot-uidlist.UIDVALIDITYの取得
        #----------------------------------------------------------------------
        # 初期化
        uidtop = []
        uidlist = {}
        # dovecot-uidlist取得
        if get_uidlist(uidtop, uidlist, uidlist_local, uidlist_lock):
            # 異常終了
            return(True)

        #----------------------------------------------------------------------
        #   UIDの辞書比較
        #----------------------------------------------------------------------
        # メール件数の取得
        mail_count = pop3.stat()[0]
        # 繰り返し
        for idx1 in range(1, mail_count + 1):
            # LIST
            list = pop3.list(idx1).decode()
            # デバック表示
            if debug:
                # 差出人
                print('LIST:' + list)

            # UIDL
            uidl = pop3.uidl(idx1).decode()
            # デバック表示
            if debug:
                # 差出人
                print('UIDL:' + uidl)

            # メール番号
            mail_num = uidl.split()[1]
            # メールUID
            mail_uidl = uidl.split()[2]

            # キーの存在判定
            if mail_uidl in uidlist:
                # 続行
                continue

            # UID(16進数→10進数)
            xuid = int(mail_uidl[0:8], 16)
            # UIDVALIDITY(16進数→10進数)
            uidv = int(mail_uidl[8:16], 16)

            #------------------------------------------------------------------
            #   メッセージ解析
            #------------------------------------------------------------------
            # メッセージの解析
            mail = pop3mail(pop3, idx1)

            #------------------------------------------------------------------
            #   ファイル名の組み立て
            #------------------------------------------------------------------
            # 受信日時(UNIX TIME)
            filename = mail.timestamp + '.'
            # マイクロ秒
            filename = filename + 'M' + str(datetime.datetime.now().microsecond)
            # プロセスID
            filename = filename + 'P' + str(os.getpid()) + '.'
            # ホスト名
            filename = filename + socket.gethostname() + ','
            # メッセージサイズ
            filename = filename +  'S=' + str(mail.size) + ','
            # 未読メール
            filename = filename +  'W=' + str(mail.wsize) + ':2'

            #------------------------------------------------------------------
            #   dovecot-uidlist.UIDVALIDITYへの出力
            #------------------------------------------------------------------
            try:
                # ファイルオープン(追記)
                fn = open(uidlist_local, 'a')

                # ファイル名の書き込み
                fn.write(str(xuid) + ' :' + filename + '\n')

            except Exception as e:
                # エラー表示
                print('{0}'.format(e))
                # 異常終了
                return(True)

            finally:
                # ファイルクローズ
                fn.close()

            #------------------------------------------------------------------
            #   メールファイルの作成
            #------------------------------------------------------------------
            try:
                # ファイルオープン(新規)
                fn = open(tmp_dir + filename, 'w')

                # メッセージの書き込み
                fn.write(mail.message)

            except Exception as e:
                # エラー表示
                print('{0}'.format(e))
                # 異常終了
                return(True)

            finally:
                # ファイルクローズ
                fn.close()

            #------------------------------------------------------------------
            #   ファイル日付の変更
            #------------------------------------------------------------------
            try:
                # 受信日時の取得
                atime = mtime = int(mail.timestamp)

                # ファイル日時の変更
                os.utime(tmp_dir + filename, (atime, mtime))

            except Exception as e:
                # エラー表示
                print('{0}'.format(e))
                # 異常終了
                return(True)

            #------------------------------------------------------------------
            #   ファイルの移動
            #------------------------------------------------------------------
            try:
                # ファイルの移動
                shutil.move(tmp_dir + filename, new_dir + filename)

            except Exception as e:
                # エラー表示
                print('{0}'.format(e))
                # 異常終了
                return(True)

            #------------------------------------------------------------------
            #   受信結果の表示
            #------------------------------------------------------------------
            try:
                # 差出人
                print('From   :' + mail.mailfrom)
            except Exception as e:
                # エラー表示
                print('{0}'.format(e))

            try:
                # タイトル
                print('Subject:' + mail.subject)
            except Exception as e:
                # エラー表示
                print('{0}'.format(e))

            try:
                # サイズ
                print('Size   :' + str(mail.size) + ' bytes')
            except Exception as e:
                # エラー表示
                print('{0}'.format(e))

    except Exception as e:
        # エラー表示
        print('{0}'.format(e))

    finally:
        # QUIT終了
        pop3.quit()

    # 正常終了
    return(False)

#------------------------------------------------------------------------------
#
#   主処理
#
#------------------------------------------------------------------------------
# 主処理
if __name__ == '__main__':
    main()

#------------------------------------------------------------------------------
