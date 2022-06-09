#------------------------------------------------------------------------------
#
#    関数名 : rotate_log
#
#    内  容 : ログファイルのローテーション
#
#    引  数 : 1) ログファイルパス
#             2) 最大ローテーション数
#
#    戻り値 : なし
#
#------------------------------------------------------------------------------
function rotate_log() {
    # ログファイル
    local _logfile=$1
    # 最大ログ数
    if [ "$2" != "" ];then
        local _logmax=$2
    else
        local _logmax=9
    fi
    # ログローテーション
    if [ -e "${_logfile}" ];then
        # 最大ログ数
        local _idx1=${_logmax}
        # 過去ログのローテーション
        while [ ${_idx1} -gt 1 ]
        do
            local _idx2=$((_idx1 - 1))
            if [ -e "${_logfile}.${_idx2}" ];then
                /bin/mv -f ${_logfile}.${_idx2} ${_logfile}.${_idx1}
            fi
            _idx1=${_idx2}
        done
        # 最新ログのローテーション
        /bin/mv -f ${_logfile} ${_logfile}.${_idx1}
    fi

    # 正常終了
    return 0
}

#------------------------------------------------------------------------------
#
#    関数名 : check_pid
#
#    内  容 : プロセス実行中の判定
#
#    引  数 : 1) PIDファイルパス
#             2) プロセス名
#
#    戻り値 : 0 : 未実行
#             1 : 実行中
#
#------------------------------------------------------------------------------
function check_pid() {
    # PIDファイル
    local _pid=$1
    # プロセス名
    if [ "$2" != "" ];then
        local _proc=$2
    else
        local _proc=$(basename $0)
    fi

    # PIDファイルが無し
    if [ ! -e ${_pid} ];then
        local _comm=""
        # PIDファイルが存在
    else
        # プロセス実行中の判定
        while read _line
        do
            _comm=$(ps -p ${_line} -o comm=)
            break
        done < ${_pid}
    fi

    # プロセス未実行
    if [ "${_comm}" != "${_proc}" ];then
        return 0
    # プロセス実行中
    else
        return 1
    fi
}

#------------------------------------------------------------------------------
#
#    関数名 : put_log
#
#    内  容 : ログファイルの書き込み
#
#    引  数 : 1) ログファイルパス
#             2) ログ内容
#
#    戻り値 : 0 : 正常終了
#             1 : 異常終了
#
#------------------------------------------------------------------------------
function put_log() {
    # 引数チェック
    if [ "$1" != "" ];then
        # ログファイル名
        local _logfile=$1
        # ログ内容
        local _logstr=" $2"

        # 日付フォーマット
        local _now=`date '+%Y-%m-%d %T'`

        # ログ出力
        echo "${_now}${_logstr}" >> ${_logfile}

        # 正常終了
        return 0
    else
        # 異常終了
        return 1
    fi
}

#------------------------------------------------------------------------------
#
#    関数名 : sec2time
#
#    内  容 : 秒をhh:mm:ssに変換
#
#    引  数 : 1) 秒数
#
#    戻り値 : hh:mm:ss
#
#------------------------------------------------------------------------------
function sec2time() {
    # 引数チェック
    if [ "$1" != "" ];then
        # 秒数
        local _sec=$1

        # hh計算
        local _hh=$((_sec / 3600))
        if [ ${_hh} -lt 10 ];then
            _hh="0"${_hh}
        fi
        # mm計算
        _sec=$((_sec % 3600))
        local _mm=$((_sec / 60))
        if [ ${_mm} -lt 10 ];then
            _mm="0"${_mm}
        fi
        # ss計算
        local _ss=$((_sec % 60))
        if [ ${_ss} -lt 10 ];then
            _ss="0"${_ss}
        fi

        # 戻り値
        echo "${_hh}:${_mm}:${_ss}"

        # 正常終了
        return 0
    fi
}
