import glob
import pandas as pd 
import sys
import math

import warnings

import os
from os import path, makedirs
import csv
import numpy as np
#np.seterr(divide='ignore', invalid='ignore')
import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import confusion_matrix, precision_score, recall_score, accuracy_score, f1_score
from sklearn.utils.multiclass import unique_labels

input_dir = sys.argv[1]
output_dir = sys.argv[2]

#POINTS_STRATA_FILE = 'points_strata_amz.csv'
POINTS_STRATA_FILE = 'points_strata_amz_old.csv'
STRATA_FILE = 'strata_amz.csv'

#IGNORED_CLASSES = [0,31,32,25,27,23,5]
IGNORED_CLASSES = [0,31,32,30,25,23,5,29]
#IGNORED_CLASSES = [0,31,32,27,23,5]

#IGNORED_CLASSES = [0,31,32,27,23]

ALL_CLASSES = {
	3: {
		"l1_val": 1,
		"l1": "1. Bosque",
		"l2_val": 3,
		"l2": "1.1. Formación Forestal",
		#"l3_val": 3,
		#"l3": "1.1. Formación Forestal"
	},
	4: {
		"l1_val": 1,
		"l1": "1. Bosque",
		"l2_val": 4,
		"l2": "1.2. Formación Sabánica",
		#"l3_val": 4,
		#"l3": "1.2. Formación Sabánica"
	},
	5: {
		"l1_val": 1,
		"l1": "1. Bosque",
		"l2_val": 5,
		"l2": "1.3. Manglar",
		#"l3_val": 5,
		#"l3": "1.3. Manglar"
	},
	6: {
		"l1_val": 1,
		"l1": "1. Bosque",
		"l2_val": 6,
		"l2": "1.4. Bosque Inundable",
		#"l3_val": 6,
		#"l3": "1.4. Bosque Inundable"
	},
	9: {
		"l1_val": 14,
		"l1": "3. Agropecuaria y Silvicultura",
		"l2_val": 9,
		"l2": "3.3. Silvicultura",
		#"l3_val": 14,
		#"l3": "3. Uso agropecuario"
		},
	10: {
		"l1_val": 10,
		"l1": "2. Formación Natural no Forestal",
		"l2_val": 10,
		"l2": "2. Formación Natural no Forestal",
		#"l3_val": 10,
		#"l3": "2. Formación Natural no Forestal"
	},
	11: {
		"l1_val": 10,
		"l1": "2. Formación Natural no Forestal",
		"l2_val": 11,
		"l2": "2.1. Formación Natural No Forestal Inundable",
		#"l3_val": 11,
		#"l3": "2.1. Formación Natural No Forestal Inundable"
	},
	12: {
		"l1_val": 10,
		"l1": "2. Formación Natural no Forestal",
		"l2_val": 12,
		"l2": "2.2. Formación Campestre o Herbazal",
		#"l3_val": 12,
		#"l3": "2.2. Formación Campestre o Herbazal"
	},
	13: {
		"l1_val": 10,
		"l1": "2. Formación Natural no Forestal",
		"l2_val": 13,
		"l2": "2.5. Otras Formaciones Naturales No Forestales",
		#"l3_val": 13,
		#"l3": "2.5. Otras Formaciones Naturales No Forestales"
	},
	14: {
		"l1_val": 14,
		"l1": "3. Agropecuaria y Silvicultura",
		"l2_val": 14,
		"l2": "3. Agropecuaria y Silvicultura",
		#"l3_val": 14,
		#"l3": "3. Agropecuaria y Silvicultura"
		},
	15: {
		"l1_val": 14,
		"l1": "3. Agropecuaria y Silvicultura",
		"l2_val": 15,
		"l2": "3.1. Pasto",
		#"l3_val": 14,
		#"l3": "3. Agropecuaria y Silvicultura"
		},
	18: {
		"l1_val": 14,
		"l1": "3. Agropecuaria y Silvicultura",
		"l2_val": 18,
		"l2": "3.2. Agricultura",
		#"l3_val": 14,
		#"l3": "3. Uso agropecuario"
		},
	21: {
		"l1_val": 14,
		"l1": "3. Agropecuaria y Silvicultura",
		"l2_val": 21,
		"l2": "3.5. Mosaico de Agricultura y/o Pastos",
		#"l3_val": 14,
		#"l3": "3. Uso agropecuario"
		},
	22: {
		"l1_val": 22,
		"l1": "4. Área sin Vegetación",
		"l2_val": 22,
		"l2": "4. Área sin Vegetación",
		#"l3_val": 22,
		#"l3": "4. Área sin Vegetación"
	},
	24: {
		"l1_val": 22,
		"l1": "4. Área sin Vegetación",
		"l2_val": 24,
		"l2": "4.1. Infraestructura Urbana",
		#"l3_val": 24,
		#"l3": "4.1. Infraestructura Urbana"
	},
	25: {
		"l1_val": 22,
		"l1": "4. Área sin Vegetación",
		"l2_val": 25,
		"l2": "4.2. Otras Áreas Sin Vegetación",
		#"l3_val": 25,
		#"l3": "4.2. Otras Áreas Sin Vegetación"
	},
	27: {
		"l1_val": 27,
		"l1": "6. No Observado",
		"l2_val": 27,
		"l2": "6. No Observado",
		#"l3_val": 27,
		#"l3": "6. No Observado"
	},
	29: {
		"l1_val": 10,
		"l1": "2. Formación Natural no Forestal",
		"l2_val": 29,
		"l2": "2.4. Afloramiento Rocosos",
		#"l3_val": 29,
		#"l3": "2.4. Afloramiento Rocosos"
	},
	30: {
		"l1_val": 22,
		"l1": "4. Área sin Vegetación",
		"l2_val": 30,
		"l2": "4.3. Minería",
		#"l3_val": 30,
		#"l3": "4.3 Minería"
	},
	33: {
		"l1_val": 26,
		"l1": "5. Cuerpos de agua",
		"l2_val": 33,
		"l2": "5.1. Río, Lago u Océano",
		#"l3_val": 33,
		#"l3": "5.1. Río, Lago u Océano"
	},
	34: {
		"l1_val": 26,
		"l1": "5. Cuerpos de agua",
		"l2_val": 34,
		"l2": "5.2. Glaciar",
		#"l3_val": 34,
		#"l3": "5.2. Glaciar"
	},
	35: {
		"l1_val": 14,
		"l1": "3. Agropecuaria y Silvicultura",
		"l2_val": 35,
		"l2": "3.4. Palma Aceitera",
		#"l3_val": 14,
		#"l3": "3. Uso agropecuario"
	},
}

def get_classes(df, level='l3'):

	class_values = {}
	class_names = {}

	clas_classes = pd.Index(df['classification'].unique())
	ref_classes = pd.Index(df['reference'].unique())

	acc_classes = clas_classes.intersection(ref_classes)

	val_remap = {}

	for value in ALL_CLASSES.keys():
		if (value not in IGNORED_CLASSES and (value in acc_classes)):
			
			val_key = "%s_val" % (level)
			new_val = ALL_CLASSES[value][val_key]
			class_name = ALL_CLASSES[value][level]

			val_remap[value] = new_val
			class_values[new_val] = True
			class_names[class_name] = True

	df = df[df['classification'].isin(val_remap.keys())]
	df = df[df['reference'].isin(val_remap.keys())]

	df['classification'] = df['classification'].map(val_remap)
	df['reference'] = df['reference'].map(val_remap)
	class_values = list(class_values.keys())
	class_names = list(class_names.keys())

	return df, class_values, class_names

def read_csvs():
	
	df_array = []
	points_strata = pd.read_csv(POINTS_STRATA_FILE)

	for csv in glob.glob(input_dir + "/*.csv"):
		df_csv = pd.read_csv(csv)
		print("Reading " + csv, df_csv.shape)
		df_array.append( df_csv )

	df = pd.concat(df_array)
	df = pd.merge(df, points_strata, how='inner', on='N_TGRT_ID')
	
	df = calculate_prob(df)

	return df

def classification_report_shinny(df, level, class_names, class_values, region, year, area_out = None):
	
	header = []
	rows = []
	footer = []

	#df = df[df['reference'].isin(class_values) | df['classification'].isin(class_values)]

	y_true = df[['reference']].to_numpy().flatten()
	y_pred = df[['classification']].to_numpy().flatten()

	sample_weight = 1 / df[['NEW_PROB']].to_numpy().flatten()

	#print(len(np.unique(y_true)),len(np.unique(y_pred)))

	y_true = np.nan_to_num(y_true)
	y_pred = np.nan_to_num(y_pred)
	sample_weight = np.nan_to_num(sample_weight)

	#print('passing at the level:',level,year)
	#print(len(y_true),len(y_pred),len(sample_weight))

	matrix = confusion_matrix(y_true, y_pred, sample_weight=sample_weight)

	#print(matrix.shape)

	glob_acc, glob_se = global_acc(df)

	user_acc, prod_acc, user_se, prod_se = user_prod_acc(df, class_values)
	refarea_prop, refarea_se = refarea_pop(df, class_values)
	map_bias, map_bias_se = calc_map_bias(df, class_values)

	matrix = matrix.transpose()
	estimated_pop = sample_weight.sum()

	matrix = (matrix / estimated_pop)

	header = [' ']
	header += class_names
	header += ["total", "population", "population bias"]
	header += ["user's accuracy", "user stderr"]
	header += ["error of comission", "area dis"]

	total_col = matrix.sum(axis=0)
	total_row = matrix.sum(axis=1)

	user_acc_tot = np.sum(user_acc * total_row)
	user_se_tot = np.sum(user_se * total_row)

	prod_acc_tot = np.sum(prod_acc * total_col)
	prod_se_tot = np.sum(prod_se * total_col)

	quantity_dis = np.absolute(total_row - total_col)
	allocation_dis = 2 * np.minimum((total_row - np.diagonal(matrix)), (total_col - np.diagonal(matrix)))

	quantity_dis_tot = np.sum(quantity_dis) / 2
	allocation_dis_tot = np.sum(allocation_dis) / 2

	#print(str(level) + ';' + region + ';' + str(glob_acc*100) + ';' + str(quantity_dis_tot*100) + ';' + str(allocation_dis_tot*100))

	dfStructure = pd.DataFrame({
		'Clase':np.append(class_names,'TOTAL'),
		'Region':np.repeat(region,len(class_names)+1),
		'Nivel': np.repeat(level,len(class_names)+1),
		'Year':np.repeat(year,len(class_names)+1),
		'Pop_Prop':np.append(total_row,1),
		'Pop_Bias': np.append(map_bias,0),
		'Pop_Bias_SE':np.append(map_bias_se,sum(map_bias_se)),
		'Global_Acc': np.append(np.repeat(0,len(class_names)),glob_acc),
		'Allocation_Tot': np.append(allocation_dis,allocation_dis_tot),
		'Quantity_Tot': np.append(quantity_dis,quantity_dis_tot),
		'Producer_Acc':np.append(prod_acc,prod_acc_tot),
		'Producer_stdErr':np.append(prod_se,prod_se_tot),
		'User_Acc':np.append(user_acc,user_acc_tot),
		'User_stdErr':np.append(user_se,user_se_tot)
	})

	area_out = pd.concat([area_out,dfStructure],ignore_index=True)

	fmt = '.3f'
	metric_fmt = '.3f'
	for i in range(matrix.shape[0]):
		row = [class_names[i]]
		for j in range(matrix.shape[1]):
			row.append(matrix[i, j])
		row.append(total_row[i])
		row.append(total_row[i])
		row.append(map_bias[i])
		row.append(user_acc[i])
		row.append(user_se[i])
		row.append((1 - user_acc[i]))
		row.append( quantity_dis[i] )

		rows.append(row)

	na_fill = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']
	
	total = ['total']
	total += ( col for col in total_col.tolist())
	total += [ np.sum(refarea_prop), np.sum(refarea_prop), 0, user_acc_tot, user_se_tot, (1-user_acc_tot), quantity_dis_tot ]

	r_adj_pop = ['adj population']
	r_adj_pop += ( col for col in refarea_prop)
	r_adj_pop += [np.sum(refarea_prop)]
	r_adj_pop += na_fill

	r_adj_pop_se = ['adj pop stdErr']
	r_adj_pop_se += ( col for col in refarea_se)
	r_adj_pop_se += [np.sum(refarea_se)]
	r_adj_pop_se += na_fill
	
	r_prod_acc = ["producer's accuracy"]
	r_prod_acc += ( col for col in prod_acc)
	r_prod_acc += [prod_acc_tot]
	r_prod_acc += na_fill

	r_prod_se = ["prod stdErr"]
	r_prod_se += ( col for col in prod_se)
	r_prod_se += [prod_se_tot]
	r_prod_se += na_fill

	r_omiss = ["error of omission"]
	r_omiss += ( (1 - col) for col in prod_se)
	r_omiss += [(1 - prod_acc_tot)]
	r_omiss += na_fill

	r_alloc_dis = ["alloc dis"]
	r_alloc_dis += ( col for col in allocation_dis)
	r_alloc_dis += [allocation_dis_tot]
	r_alloc_dis += na_fill

	result = [[" "]]
	result += [[" "]]
	result += [[" ANO: " + str(year) + " "]]
	result += [header]
	result += rows
	result += [total]
	result += [r_adj_pop]
	result += [r_adj_pop_se]
	result += [r_prod_acc]
	result += [r_prod_se]
	result += [r_omiss]
	result += [r_alloc_dis]

	return result,area_out

def save_csv(output_filename, data):
	with open(output_filename, encoding='latin-1', mode='w',newline='') as output_file:
		print("Generating " + output_filename)
		csv_writer = csv.writer(output_file, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
		csv_writer.writerows(data)

def calculate_prob(df):
	strata = pd.read_csv(STRATA_FILE)
	df = pd.merge(df, strata, how='inner', on="strata_id")

	samples = df['strata_id'].value_counts().rename_axis('strata_id').reset_index(name='n_samp')
	df = pd.merge(samples, df, on='strata_id')
	#df['NEW_PROB'] = df['n_samp'] / df['pop']

	biomes = df['COUNTRY'].unique()

	for biome in biomes:
		biome_filter = (df['COUNTRY'] == biome)
		n_samples, _ = df[biome_filter & (df['AMOSTRAS'] != 'treinamento')].shape
		t_samples, _ = df[biome_filter].shape
		 
		prob_biome_adjs = n_samples / t_samples
		df.loc[biome_filter, 'NEW_PROB'] = df[biome_filter]['NEW_PROB'] * prob_biome_adjs

	return df[df['AMOSTRAS'] != 'treinamento']

def mkdirp(path):
	try:
		makedirs(path)
	except:
		pass

def accuracy_assessment_all(df, biome='Amazonía', area_out = None):
	
	for level in ['l2', 'l1']: #,'l3']

		acc_output_dir = path.join(output_dir, level)
		mkdirp(acc_output_dir)

		output_filename = path.join(acc_output_dir, ''.join(['acc_int_', str(biome), '.csv']))

		years = df['year'].unique()
		years.sort()

		result = [["Thu Jan 23 16:36 2021   Matrizes de confusão anuais para " + biome + "  -  Coleção 3.0 (CLASSIFICAÇÃO + FILTRO + INTEGRAÇÃO)  "]]
		result += [[" "]]
		result += [["Corpo da tabela contém distribuição de frequências cruzadas da amostra."]]
		result += [["Marginais:"]]
		result += [["Totais: A coluna 'total' contém a soma das amostras de cada classe mapeada ou a estatística de linha para todas as classes. A linha 'total' contém a soma das amostras em cada classe observada ou a respectiva estatística de coluna para todas as classes. "]]
		result += [["Número de píxeis na população - A coluna 'population' contém o número de píxeis totais de cada classe mapeada. A 'adj population' contém as estimativas no número de píxeis na população corrigida pela matriz de erros. A coluna 'bias' contém a estimativa do viés relativo da área mapeada. A linha 'adj pop stdErr' contém uma estimativa do erro padrão do número de píxeis corrigido. Usado para representar a incerteza d ou construir intervalos de confiança. A estimativa do erro padrão é confiável apenas quando n>30./nAcurácias - Acurácia do usuário (user's accuracy): estimativa da fração de píxeis (ou área) de cada classe do mapa que está corretamente mapeada. Acurácia do produtor (producer's accuracy): estimativa da fração de píxeis (ou área) de cada classe que foi corretamente mapeada. A coluna 'user stderr' contém a estimativa do erro padrão da acurácia do usuário"]]
		result += [["Erros - Erro de comissão e omissão: são os complementares da acurácia do usuário e produtor"]]
		result += [["Decomposição do erro - O erro é decomposto em 'discordância de área' (area dis) e 'discordância de alocação' (alloc dis). A soma deles é o erro total."]]

		for year in years:

			if int(year) > 2018 and biome == "Brazil":
				continue

			result_raw , area_out = accuracy_assessment(df, level, year, biome, area_out)
			result += result_raw

		result_raw , area_out = accuracy_assessment(df, level, 'Todos', biome, area_out)
		result += result_raw

		save_csv(output_filename, result)

	return area_out

def accuracy_assessment(df, level='l2', year='Todos', biome='Amazonía', area_out = None):

	df = df.copy(deep=True)
	
	if year != 'Todos':
		df = df[df['year'] == year]

	if biome != 'Amazonía':
		df = df[df['COUNTRY'] == biome]
	else:
		df = df[df['COUNTRY'] != 'Brazil']
	
	df, class_values, class_names = get_classes(df, level)

	return classification_report_shinny(df, level, class_names, class_values, biome, year, area_out)

def population_estimation(df):
	sample_weight = 1.0 / df[['NEW_PROB']].to_numpy().flatten()
	return sample_weight.sum()

def covariance(x, y):
	if x.size < 1:
		x_mean = np.mean(x)
		y_mean = np.mean(y)

		return np.sum((x - x_mean) * (y - y_mean) / (x.size - 1))
	else:
		return 0.0

def user_prod_se(df, class_val, user_acc, prod_acc, map_total, ref_total):
	
	user_var = 0
	prod_var = 0

	user_se = 0
	prod_se = 0

	for name, df_strata in df.groupby('strata_id'):
		ref_val_s = df_strata['reference'].to_numpy()
		map_val_s = df_strata['classification'].to_numpy()

		map_total_s = np.where((map_val_s == class_val), 1, 0)
		map_correct_s = np.where(np.logical_and((map_val_s == class_val),(map_val_s == ref_val_s)), 1, 0)

		ref_total_s = np.where((ref_val_s == class_val), 1, 0)
		ref_correct_s = np.where(np.logical_and((ref_val_s == class_val),(map_val_s == ref_val_s)), 1, 0)
		
		nsamples_s, _ = df_strata.shape
		population_s = population_estimation(df_strata)

		user_var += math.pow(population_s,2) * (1 - nsamples_s/population_s) \
									* ( math.pow(	np.var(map_correct_s) , 2) \
											+ math.pow(user_acc,2) * math.pow( np.var(map_total_s) , 2) \
											- 2 * user_acc * covariance(map_total_s, map_correct_s) \
 										) / nsamples_s

		prod_var += math.pow(population_s,2) * (1 - nsamples_s/population_s) \
									* ( math.pow(	np.var(ref_correct_s) , 2) \
											+ math.pow(prod_acc,2) * math.pow( np.var(ref_total_s) , 2) \
											- 2 * prod_acc * covariance(ref_total_s, ref_correct_s) \
 										) / nsamples_s

	if (map_total !=0):
		user_var = 1 / math.pow(map_total,2) * user_var
		user_se = 1.96 * math.sqrt(user_var)

	if (ref_total !=0):
		prod_var = 1 / math.pow(ref_total,2) * prod_var
		prod_se = 1.96 * math.sqrt(prod_var)

	return user_se, prod_se

def global_se(df, mask, population):
	glob_var = 0

	for name, df_strata in df.groupby('strata_id'):
		ref_val_s = df['reference'].to_numpy()
		map_val_s = df['classification'].to_numpy()

		map_correct_s = np.where(mask, 1, 0)

		nsamples_s, _ = df_strata.shape
		population_s = population_estimation(df_strata)
		
		glob_var += math.pow(population_s,2) * (1 - nsamples_s/population_s) \
								* np.var(map_correct_s) / nsamples_s

	glob_var = ((1.0 / float(math.pow(population,2.0))) * float(glob_var)) if float(math.pow(population,2.0)) != 0 else 0
	glob_se = 1.96 * float(math.sqrt(float(glob_var)))

	return glob_se

def calc_map_bias(df, class_values):

	map_bias_arr = []
	map_bias_se_arr = []

	ref_val = df['reference'].to_numpy()
	map_val = df['classification'].to_numpy()
	samp_weight = 1 / df['NEW_PROB'].to_numpy()

	population = population_estimation(df)

	for class_val in class_values:
	
		map_mask = np.logical_and((map_val == class_val), (ref_val != class_val))
		map_comission_prop = np.sum(np.where(map_mask, 1, 0) * samp_weight) / population

		ref_mask = np.logical_and((ref_val == class_val), (map_val != class_val))
		map_omission_prop = np.sum(np.where(ref_mask, 1, 0) * samp_weight) / population

		map_bias = (map_omission_prop - map_comission_prop)
		
		se_mask = np.logical_xor(ref_mask,map_mask)
		map_bias_se = global_se(df, se_mask, population)

		map_bias_arr.append(map_bias)
		map_bias_se_arr.append(map_bias_se)

	return map_bias_arr, map_bias_se_arr

def refarea_pop(df, class_values):

	refarea_prop_arr = []
	refarea_se_arr = []

	ref_val = df['reference'].to_numpy()
	map_val = df['classification'].to_numpy()
	samp_weight = 1 / df['NEW_PROB'].to_numpy()

	population = population_estimation(df)

	for class_val in class_values:
	
		ref_mask = (ref_val == class_val)
		refarea = np.sum(np.where(ref_mask, 1, 0) * samp_weight)

		refarea_prop = (refarea / population)
		refarea_se = global_se(df, ref_mask, population)

		refarea_prop_arr.append(refarea_prop)
		refarea_se_arr.append(refarea_se)

	return refarea_prop_arr, refarea_se_arr

def global_acc(df):

	ref_val = df['reference'].to_numpy()
	map_val = df['classification'].to_numpy()
	samp_weight = 1 / df['NEW_PROB'].to_numpy()
	
	mask_correct = (map_val == ref_val)
	map_correct = np.sum(np.where(mask_correct, 1, 0) * samp_weight)
	population = population_estimation(df)

	glob_acc = (map_correct / population)

	glob_acc = glob_acc
	glob_se = global_se(df, mask_correct, population)

	return glob_acc, glob_se

def user_prod_acc(df, class_values):

	user_acc_arr = []
	prod_acc_arr = []
	user_se_arr = []
	prod_se_arr = []

	ref_val = df['reference'].to_numpy()
	map_val = df['classification'].to_numpy()
	samp_weight = 1.0 / df['NEW_PROB'].to_numpy()

	for class_val in class_values:

		map_total = np.sum(np.where((map_val == class_val), 1, 0) * samp_weight)
		map_correct = np.sum(np.where(np.logical_and((map_val == class_val),(map_val == ref_val)), 1, 0) * samp_weight)

		ref_total = np.sum(np.where((ref_val == class_val), 1, 0) * samp_weight)
		ref_correct = np.sum(np.where(np.logical_and((ref_val == class_val),(map_val == ref_val)), 1, 0) * samp_weight)

		user_acc = 0
		if map_total > 0:
			user_acc = map_correct / map_total

		prod_acc = 0
		if ref_total > 0:
			prod_acc = ref_correct / ref_total

		user_se, prod_se = user_prod_se(df, class_val, user_acc, prod_acc, map_total, ref_total)

		user_acc_arr.append(user_acc)
		prod_acc_arr.append(prod_acc)
		user_se_arr.append(user_se)
		prod_se_arr.append(prod_se)

	return user_acc_arr, prod_acc_arr, user_se_arr, prod_se_arr

def config_class_21(df):
	agro_filter = (df['classification'] == 21) & (df['reference'].isin([15,18,21]))
	#agro_filter = (df['reference'] == 21)
	df.loc[agro_filter, 'reference'] = 21
	df.loc[(df['reference'] == 21) & (df['classification']==24), 'classification'] = 21

	return df

df = read_csvs()

#df.loc[ (df['NEW_PROB'] == 0.0), 'NEW_PROB'] = float("%0.10f" % (1.0/df.iloc[[2]]['PESO_AMOS']*df.iloc[[2]]['ADJ_FACTOR']))

total_points = population_estimation(df)

#df = df[df['POINTEDITE'] == False]

df = config_class_21(df)

regions = df['COUNTRY'].unique().tolist()
regions.append('Amazonía')

print(regions)

#areaEstimatives = pd.DataFrame({'Clase':[],'Region':[],'Level':[],'Year':[],'Pop_Prop':[],'Pop_Bias':[],'Pop_Bias_SE':[]})
areaEstimatives = pd.DataFrame({
	'Clase':[],'Region':[],'Nivel':[],
	'Year':[],'Pop_Prop':[],'Pop_Bias':[],
	'Pop_Bias_SE':[],'Global_Acc':[],'Allocation_Tot':[],
	'Quantity_Tot':[],'Producer_Acc':[],'Producer_stdErr':[],
	'User_Acc':[],'User_stdErr':[]
})

output_area_name = path.join(output_dir, ''.join(['col4_stats_Amazonía.csv']))


for region in regions:

	if region in ['Brazil','Colombia', 'Guyana', 'Suriname']:
		continue

	#print(region)

	areaEstimatives =None
	areaEstimatives = accuracy_assessment_all(df, region, areaEstimatives)

	hdr_v2 = False  if os.path.isfile(output_area_name) else True
	areaEstimatives.to_csv(output_area_name,mode='a',header = hdr_v2,index = False)

	#accuracy_assessment_all(df, region)