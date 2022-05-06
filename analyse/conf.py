jars = ['./analyse/jdbc/ifxjdbc.jar','./analyse/jdbc/postgresql-42.3.4.jar']
jdbc = {
    'Informix': {
        'clazz': 'com.informix.jdbc.IfxDriver',
        'connectStr': 'jdbc:informix-sqli://{host}:{port}/{dbname}:informixserver={servername};'
                      'DB_LOCALE=en_us.819;CLIENT_LOCALE=en_us.57372;NEWCODESET=GBK,8859-1,819'
    },
    'PostgreSQL': {
        'clazz': 'org.postgresql.Driver',
        'connectStr': 'jdbc:postgresql://localhost:5432/{dbname}'
    }
}
