#! /bin/bash
SERVICE=svrchan

dump() 
{
    VARNAME=$1
    VARVAL=`eval echo '$'"$VARNAME"`
    DEFAULT="(default: $2)"
    printf "    %15s = %-35s %s\n" "$VARNAME" "$VARVAL" "$DEFAULT"
}

usage()
{
    echo ================================================================================
    echo "请为docker添加以下环境变量 (如果直接使用python，请在变量前加上前缀 SVRCHAN_ )"
    dump 'MAIL_FROM' 'Henry TIAN <chariothy@gmail.com>'
    dump 'MAIL_FROM' 'Henry TIAN <chariothy@gmail.com>'
    dump 'MAIL_TO' 'Henry TIAN <chariothy@gmail.com>'
    dump 'SMTP_HOST' 'smtp.gmail.com'
    dump 'SMTP_PORT' 25
    dump 'SMTP_USER' 'chariothy@gmail.com'
    dump 'SMTP_PWD'
    dump 'SVRCHAN_WATCH' '1'
    dump 'DINGTALK_TOKEN'
    dump 'DINGTALK_SECRET'
    echo ================================================================================
}

warn_debug() 
{
    echo ===============================================
    echo -e "\033[5;34m!!!!!!!!!!!! Running in DEBUG mode !!!!!!!!!!!!\033[0m"
    echo ===============================================
}

usage

if [[ -z $SMTP_PWD || -z $DINGTALK_TOKEN || -z $DINGTALK_SECRET ]];then
    exit 1
fi

if [ "$ENV" == "prod" ]; then
        docker-compose down
        docker-compose up -d \
    &&  docker-compose logs -f --tail=10
else
        docker-compose build \
            --build-arg UNAME=$(whoami) \
            --build-arg UID=$(id -u) \
            --build-arg GID=$(id -g) \
    &&  warn_debug \
    &&  docker-compose up
fi