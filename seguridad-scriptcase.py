import os, pymssql, pandas as pd
# assign directory
directory = r'c:\temp'

conn = pymssql.connect(server="sp01",user="sa",password="FdN2015",database="Indicadores18042022")
cursor = conn.cursor()
cursor2 = conn.cursor()

query = """
    delete from lda_users_apps;
insert into lda_users_apps(app_name, login, priv_access, priv_insert, priv_delete, priv_update, priv_export, priv_print)
SELECT [app_name]
	  	  ,u.username
      ,max([priv_access])
      ,max([priv_insert])
      ,max([priv_delete])
      ,max([priv_update])
      ,max([priv_export])
      ,max([priv_print])

  FROM [Indicadores18042022].[dbo].[lda_grupo_apps]
	inner join auth_user_groups aug on grupo=aug.group_id
	inner join auth_user u on aug.user_id=u.id
where priv_access is not null
group by [app_name]
	  , u.username
"""
cursor.execute(query)

