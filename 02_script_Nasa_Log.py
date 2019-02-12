# Datasets:
# Database July 	-> ftp://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz
# Database August 	-> ftp://ita.ee.lbl.gov/traces/NASA_access_log_Aug95.gz


from pyspark import SparkConf, SparkContext
from operator import add


conf = (SparkConf()
         .setMaster("local")
         .setAppName("SPark")
         .set("spark.executor.memory", "2g"))
sc = SparkContext(conf = conf)


july = sc.textFile('Nasa_access_log_Jul95')
july = july.cache()

august = sc.textFile('Nasa_access_log_Aug95')
august = august.cache()


# 1-- Número de hosts únicos ou seja Distinct hosts
	july_count = july.flatMap(lambda line: line.split(' ')[0]).distinct().count()
	august_count = august.flatMap(lambda line: line.split(' ')[0]).distinct().count()
	print('Hosts unicos em Julho: %s' % july_count)
	print('Hosts unicos em Agosto %s' % august_count)


# 2-- Total de erros 404
def code_404(line):
    try:
        code = line.split(' ')[-2]
        if code == '404':
            return True
    except:
        pass
    return False
    
july_404 = july.filter(code_404).cache()
august_404 = august.filter(lambda line: line.split(' ')[-2] == '404').cache()

print('Erros 404 em Julho: %s' % july_404.count())
print('Erros 404 em Agosto %s' % august_404.count())


# 3-- 5 URLs que mais causaram erro 404.
def top5_Urls_Erro(rdd):
    extrem = rdd.map(lambda line: line.split('"')[1].split(' ')[1])
    counts = extrem.map(lambda extre: (extre, 1)).reduceByKey(add)
    top = counts.sortBy(lambda pair: -pair[1]).take(5)
    
    print('\nTop 5 URLS ERRO 404:')
    for extre, count in top:
        print(extre, count)
        
    return top

top5_Urls_Erro(july_404)
top5_Urls_Erro(august_404)


# 4-- Quantidade de erros 404 por dia.
def diaria_count(rdd):
    dias = rdd.map(lambda line: line.split('[')[1].split(':')[0])
    counts = dias.map(lambda dia: (dia, 1)).reduceByKey(add).collect()
    
    print('\n Erros 404 por dia:')
    for dia, count in counts:
        print(dia, count)
        
    return counts

diaria_count(july_404)
diaria_count(august_404)


# 5-- Total de bytes retornados 
def tot_byter_count(rdd):
    def byte_count(line):
        try:
            count = int(line.split(" ")[-1])
            if count < 0:
                raise ValueError()
            return count
        except:
            return 0
        
    count = rdd.map(byte_count).reduce(add)
    return count

print('Total de bytes retornados em Julho: %s' % tot_byter_count(july))
print('Total de bytes retornados em Agosto: %s' % tot_byter_count(august))


sc.stop()