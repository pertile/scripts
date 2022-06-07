import os, datetime as DT, time

# for subdir, dirs, files in os.walk("\\\\sp01\\digitalizacion\\documentos digitalizados"):
for subdir, dirs, files in os.walk("d:\\laracast"):
    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file
        #print(filepath)
        modificado = DT.date.fromtimestamp(os.path.getmtime(filepath))
        stats = statsbuf = os.stat(filepath)
        # print(filepath + " modificado: %s" % time.ctime(os.path.getmtime(filepath)))
        print(stats)
        # if modificado > (DT.date.today() - DT.timedelta(days=90)):
        #     print(filepath + ";" + stats.st_mtime + ";" + String.valueOf(time.ctime(os.path.getmtime(filepath))))