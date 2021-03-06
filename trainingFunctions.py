import numpy as np
from sklearn.model_selection import KFold, train_test_split, cross_validate
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error
from scipy.interpolate import interp1d
import pandas
import os
import datetime

# define base model factory
def baseline_model(inputDim, neuronsPerLayerExceptOutputLayer, learn_rate = 0.001):
	from keras.models import Sequential
	from keras.layers import Dense
	from keras import optimizers
	# create model
	def build_fn():
		regressor = Sequential()
		regressor.add(Dense(neuronsPerLayerExceptOutputLayer[0], input_dim=inputDim, activation="relu"))
		for units in neuronsPerLayerExceptOutputLayer[1:]:
			regressor.add(Dense(units, activation="relu"))
		regressor.add(Dense(1, activation="linear"))
		opt = optimizers.adam(lr=learn_rate)
		regressor.compile(optimizer=opt, loss='mean_absolute_error')
		return regressor
	return build_fn

def showGraphs(is_class, history, X_Unseen, Y_Unseen, X_test, Y_test, fileNames, args):
	from keras.models import load_model
	if is_class:
		lossFile = fileNames["directory"] + "classical_loss.png"
		testFile = fileNames["directory"] + "classical_test.png"
		unseenFile = fileNames["directory"] + "classical_unseen.png"
		lossTitle = "Classical Model Loss"
		testTitle = "Classical Test Data Performance"
		unseenTitle = "Classical Unseen Data Performance"
		# loss
		plt.plot(history.history['loss'])
		plt.plot(history.history['val_loss'])
		plt.title(lossTitle)
		plt.ylabel('Loss')
		plt.xlabel('Epoch')
		plt.legend(['train','test'], loc='upper left')
		fig = plt.gcf()
		if args["visualize"]: plt.show()
		fig.savefig(lossFile)
		plt.clf()
		Proposed_Model = load_model(fileNames["directory"] + fileNames["Best_Classical"])

	else:
		lossFile = fileNames["directory"] + "cross_loss.png"
		testFile = fileNames["directory"] + "cross_test.png"
		unseenFile = fileNames["directory"] + "cross_unseen.png"
		lossTitle = "Cross Validation Model Loss"
		testTitle = "Cross Validation Test Data Performance"
		unseenTitle = "Cross Validation Unseen Data Performance"
		# Cross validation model analysis (loss)
		plt.plot(abs(history))
		plt.title(lossTitle)
		plt.ylabel('loss')
		plt.xlabel('Fold')
		plt.legend(['train'], loc='upper left')
		fig = plt.gcf()
		if args["visualize"]: plt.show()
		fig.savefig(lossFile)
		plt.clf()
		Proposed_Model = load_model(fileNames["directory"] + fileNames["Best_Cross"])

	Y_Proposed_Test = Proposed_Model.predict(X_test)
	plt.scatter(Y_test, Y_Proposed_Test)
	plt.plot([Y_test.min(), Y_test.max()], [Y_test.min(), Y_test.max()], 'k--', lw=4)
	plt.xlabel('Measured')
	plt.ylabel('Predicted')
	plt.title(testTitle)
	fig = plt.gcf()
	if args["visualize"]: plt.show()
	fig.savefig(testFile)
	plt.clf()
	# Results
	Y_Proposed = Proposed_Model.predict(X_Unseen)
	plt.scatter(Y_Unseen, Y_Proposed)
	plt.plot([Y_Unseen.min(), Y_Unseen.max()], [Y_Unseen.min(), Y_Unseen.max()], 'k--', lw=4)
	plt.xlabel('Measured')
	plt.ylabel('Predicted')
	plt.title(unseenTitle)
	fig = plt.gcf()
	if args["visualize"]: plt.show()
	fig.savefig(unseenFile)
	plt.clf()
	return

def showBMIGraphs(history, Y_Classic, Y_Test,Y_Cross,x, directory, results):
	# loss
	plt.plot(history.history['loss'])
	plt.plot(history.history['val_loss'])
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('epoch')
	plt.legend(['train','test'], loc='upper left')
	fig = plt.gcf()
	fig.savefig(directory+'loss_run_'+str(x)+'.png')
	plt.show()
	plt.clf()

	# Cross validation model analysis (loss)
	plt.plot(results)
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('Fold')
	plt.legend(['train'], loc='upper left')
	fig = plt.gcf()
	fig.savefig(directory+'fold_run_'+str(x)+'.png')
	plt.show()
	plt.clf()

	#Classic scatter
	plt.scatter(Y_Test, Y_Classic)
	plt.plot([Y_Test.min(), Y_Test.max()], [Y_Test.min(), Y_Test.max()], 'k--', lw=4)
	plt.xlabel('Measured')
	plt.ylabel('Predicted')
	plt.title('Classic Model - Test Data')
	fig = plt.gcf()
	fig.savefig(directory+'classic_run_'+str(x)+'.png')
	plt.show()
	plt.clf()

	#Cross scatter
	plt.scatter(Y_Test, Y_Cross)
	plt.plot([Y_Test.min(), Y_Test.max()], [Y_Test.min(), Y_Test.max()], 'k--', lw=4)
	plt.xlabel('Measured')
	plt.ylabel('Predicted')
	plt.title('Cross Model - Test Data')
	fig = plt.gcf()
	fig.savefig(directory+'cross_run_'+str(x)+'.png')
	plt.show()
	plt.clf()
	return

def Final_Graphs(Y_Unseen,Y_Best_Classic,Y_Best_Cross,Full_dataset,Y_Average,Y_full, directory):

	if (Full_dataset == True):
		Classic_Path = directory + 'best_classic_full.png'
		Cross_Path = directory + 'best_cross_full.png'
	else:
		Classic_Path = directory + 'best_classic.png'
		Cross_Path = directory + 'best_cross.png'

	#Best Classic
	plt.scatter(Y_Unseen,Y_Best_Classic)
	plt.plot([Y_Unseen.min(), Y_Unseen.max()], [Y_Unseen.min(), Y_Unseen.max()], 'k--', lw=4)
	plt.xlabel('Measured')
	plt.ylabel('Predicted')
	plt.title('Final Model - Classic')
	fig = plt.gcf()
	fig.savefig(Classic_Path)
	plt.show()
	plt.clf()
	# Best Cross
	plt.scatter(Y_Unseen, Y_Best_Cross)
	plt.plot([Y_Unseen.min(), Y_Unseen.max()], [Y_Unseen.min(), Y_Unseen.max()], 'k--', lw=4)
	plt.xlabel('Measured')
	plt.ylabel('Predicted')
	plt.title('Final Model - Cross')
	fig = plt.gcf()
	fig.savefig(Cross_Path)
	plt.show()
	plt.clf()
	#Average
	if (Full_dataset==True):
		plt.scatter(Y_full, Y_Average)
		plt.plot([Y_full.min(), Y_full.max()], [Y_full.min(), Y_full.max()], 'k--', lw=4)
		plt.xlabel('Measured')
		plt.ylabel('Predicted')
		plt.title('Average')
		fig = plt.gcf()
		fig.savefig(directory + 'Average.png')
		plt.show()
		plt.clf()
	return

def overallscore(MAE, Max):
	if MAE < 4:
		m = interp1d([0,4],[4,0])
		return MAE/Max + m(MAE)
	else: return MAE/Max

def train(X, Y, args, CM, CVR , fileNames, infoFile):
	from keras.models import load_model
	Classic_Model = CM
	Cross_Val_Regressor = CVR
	best_scores = {}
	ClassHistory = None
	CrossHistory = None
	# Initialise Best Scores to be Overwritten
	best_class_score = 0
	best_cross_score = 0
	Y = Y.reshape(-1,1)
	# Separate file data into seen and unseen data prior to model comparison
	seed = 10
	np.random.seed(seed)
	X,X_Unseen,Y,Y_Unseen = train_test_split(X,Y,test_size=0.2)

	# finding optimal model
	for x in range(args["number"]):
		np.random.seed(x)
		# classic test split
		X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3)
		history = Classic_Model.fit(X_train, Y_train, batch_size=args['batch'], epochs=args['epochs'], verbose=1, validation_data=(X_test, Y_test))
		Y_Classic = Classic_Model.predict(X_test)
		Classic_Model.model.save(fileNames["Classic_Model_File"])

		# unseen data tests
		Y_Unseen_Classical = Classic_Model.predict(X_Unseen)

		# Performance indicators
		Classical_MSE = mean_squared_error(Y_Unseen, Y_Unseen_Classical)
		Classical_MAE = mean_absolute_error(Y_Unseen, Y_Unseen_Classical)
		Classical_Max = max_error(Y_Unseen, Y_Unseen_Classical)
		print('Classical MSE', str(Classical_MSE))
		print('Classical MAE', str(Classical_MAE))
		print('Classical Max', str(Classical_Max))

		Classical_Overall = overallscore(Classical_MAE, Classical_Max)

		if Classical_Overall > best_class_score:
			Classic_Model.model.save(fileNames["directory"] + fileNames["Best_Classical"])
			best_scores['Classical'] = [Classical_MAE, Classical_Max]
			best_class_score = Classical_Overall
			ClassHistory = history

	showGraphs(True, ClassHistory, X_Unseen, Y_Unseen, X_test, Y_test, fileNames, args)

	for x in range(args["number"]):
		np.random.seed(x)
		# evaluate model with dataset for Cross Validation
		if args['strat']:
			kfold = args['fold']
		else:
			kfold = KFold(n_splits=args['fold'], random_state=x)
		# Optimal estimator extraction
		Cross_Val = cross_validate(Cross_Val_Regressor, X, Y, cv=kfold, return_estimator=True, scoring='neg_mean_absolute_error')
		results = Cross_Val["test_score"]
		estimator_array = Cross_Val['estimator']
		Cross_val_estimator = estimator_array[-1]
		Cross_val_estimator.model.save(fileNames["Cross_Model_File"])
		# Assessing optimal model
		Cross_Val_Model = load_model(fileNames["Cross_Model_File"])
		Y_Cross_Val = Cross_Val_Model.predict(X_test)
		
		Y_Unseen_Cross = Cross_Val_Model.predict(X_Unseen)
		Cross_MSE = mean_squared_error(Y_Unseen, Y_Unseen_Cross)
		Cross_MAE = mean_absolute_error(Y_Unseen, Y_Unseen_Cross)
		Cross_Max = max_error(Y_Unseen, Y_Unseen_Cross)

		print('Cross MSE', str(Cross_MSE))
		print('Cross MAE', str(Cross_MAE))
		print('Cross Max', str(Cross_Max))

		Cross_Overall = overallscore(Cross_MAE, Cross_Max)
		if Cross_Overall > best_cross_score:
			Cross_Val_Model.model.save(fileNames["directory"] + fileNames["Best_Cross"])
			best_scores['Cross'] = [Cross_MAE, Cross_Max]
			best_cross_score = Cross_Overall
			CrossHistory = results
	
	showGraphs(False, CrossHistory, X_Unseen, Y_Unseen, X_test, Y_test, fileNames, args)
	if args['fold']:
		fold_string = 'Sfold'
	else:
		fold_string = 'fold'
	infoFile.write(str(best_scores))
	infoFile.write(str('\n'))
	infoFile.write(str({'Number Of Iterations': args["number"], 'Batch': args["batch"], 'Epochs': args['epochs'], fold_string: args['fold']}))
	infoFile.close()
	return

def trainWithBMI(X, Y, args, fileNames):
	from keras.wrappers.scikit_learn import KerasRegressor
	# Initialise Models and Folder Structure
	inputDim = 6
	neuronsPerLayerExceptOutputLayer = [7,4,2,1]
	build = baseline_model(inputDim, neuronsPerLayerExceptOutputLayer,0.01)
	Classic_Model = build()
	Cross_Val_Regressor = KerasRegressor(build_fn=build, epochs=args['epochs'], batch_size=args['batch'], verbose=1)

	# Created Directory
	NetworkArc = [str(row.units) for row in Classic_Model.model.layers]
	NetworkArc = '-'.join(NetworkArc)
	today = str(datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S"))
	fileNames["directory"] = 'models/' + today + '/BMI/' + NetworkArc + '/'
	os.makedirs(fileNames["directory"])

	infoFile = open(fileNames["directory"] + 'BMI-info.txt', 'w', newline='')
	train(X, Y, args, Classic_Model, Cross_Val_Regressor, fileNames, infoFile)
	return

def trainHeight(X, Y, args, fileNames):
	from keras.wrappers.scikit_learn import KerasRegressor
	print("[INFO] Training Against Height")
	# Initialise Models and Folder Structure
	inputDim = 2
	neuronsPerLayerExceptOutputLayer = [4, 3, 2]
	build = baseline_model(inputDim, neuronsPerLayerExceptOutputLayer)
	Classic_Model = build()
	Cross_Val_Regressor = KerasRegressor(build_fn=build, epochs=args['epochs'], batch_size=args['batch'], verbose=1)

	# Created Directory
	NetworkArc = [str(row.units) for row in Classic_Model.model.layers]
	NetworkArc = '-'.join(NetworkArc)
	today = str(datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S"))
	fileNames["directory"] = 'models/' + today + '/Height/' + NetworkArc + '/'
	os.makedirs(fileNames["directory"])

	# Initialise Models and Folder Structure
	infoFile = open(fileNames["directory"] + 'Height-info.txt', 'w', newline='')
	train(X, Y, args, Classic_Model, Cross_Val_Regressor, fileNames, infoFile)
	return

def trainMass(X, Y, args, fileNames):
	from keras.wrappers.scikit_learn import KerasRegressor
	print("[INFO] Training Against Mass")
	# Initialise Models and Folder Structure
	inputDim = 6
	neuronsPerLayerExceptOutputLayer = [15, 14, 13, 12, 11, 10, 9]
	build = baseline_model(inputDim, neuronsPerLayerExceptOutputLayer)
	Classic_Model = build()
	Cross_Val_Regressor = KerasRegressor(build_fn=build, epochs=args['epochs'], batch_size=args['batch'], verbose=1)

	# Created Directory
	NetworkArc = [str(row.units) for row in Classic_Model.model.layers]
	NetworkArc = '-'.join(NetworkArc)
	today = str(datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S"))
	fileNames["directory"] = 'models/' + today + '/Mass/' + NetworkArc + '/'
	os.makedirs(fileNames["directory"])

	infoFile = open(fileNames["directory"] + 'Mass-info.txt', 'w', newline='')
	train(X, Y, args, Classic_Model, Cross_Val_Regressor, fileNames, infoFile)
	return

def trainCompensator(args, Regressor, Cross_Val_Regressor, X, Y, directory, fileNames, X_Unseen, Y_Unseen):
	from keras.models import load_model

	bestscores = {}
	best_class_score = 0
	best_cross_score = 0
	ClassHistory = None
	CrossHistory = None

	# finding optimal model
	for x in range(args['iter']):
		np.random.seed(x)
		# classic test split
		X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3)
		history = Regressor.fit(X_train, Y_train, batch_size=args['batch'], epochs=args['epochs'], verbose=1, validation_data=(X_test, Y_test))
		Y_Classic = Regressor.predict(X_test)
		Regressor.model.save(fileNames["Classic_Model_File"])

		if args['strat']:
			kfold = args['fold']
			fold_string ="Sfold"
		else:
			kfold = KFold(n_splits=args['fold'], random_state=x)
			fold_string = "Fold"

		# Cross validation
		# Optimal estimator extraction
		Cross_Val = cross_validate(Cross_Val_Regressor, X, Y, cv=kfold, return_estimator=True)
		estimator_array = Cross_Val['estimator']
		results = Cross_Val['test_score']
		Lowest_Score = np.amin(results)
		Lowest_Score_Index = np.where(results==Lowest_Score)
		Cross_val_estimator = estimator_array[np.ndarray.item(Lowest_Score_Index[0])]
		Cross_val_estimator.model.save(fileNames["Cross_Model_File"])
		# Assessing optimal model
		Cross_model = load_model(fileNames["Cross_Model_File"])
		Y_Cross_Val = Cross_model.predict(X_test)
		# unseen data tests
		Y_Unseen_Classical = Regressor.predict(X_Unseen)
		Y_Unseen_Cross = Cross_model.predict(X_Unseen)
		# Performance indicators
		Classical_MSE = mean_squared_error(Y_Unseen, Y_Unseen_Classical)
		Cross_MSE = mean_squared_error(Y_Unseen, Y_Unseen_Cross)
		Classical_MAE = mean_absolute_error(Y_Unseen, Y_Unseen_Classical)
		Cross_MAE = mean_absolute_error(Y_Unseen, Y_Unseen_Cross)
		Classical_Max = max_error(Y_Unseen, Y_Unseen_Classical)
		Cross_Max = max_error(Y_Unseen, Y_Unseen_Cross)
		print(str(Classical_MSE) + "\t" + str(Cross_MSE))
		print(str(Classical_MAE) + "\t" + str(Cross_MAE))
		print(str(Classical_Max) + "\t" + str(Cross_Max))
		# save file option
		Classical_Overall = overallscore(Classical_MAE, Classical_Max)
		Cross_Overall = overallscore(Cross_MAE, Cross_Max)
		if Classical_Overall > best_class_score:
			Regressor.model.save(directory + fileNames["Best_Classic_File"])
			bestscores['Classical'] = [Classical_MAE, Classical_Max]
			best_class_score = Classical_Overall
			ClassHistory = history

		if Cross_Overall > best_cross_score:
			Cross_model.model.save(directory + fileNames["Best_Cross_File"])
			bestscores['Cross'] = [Cross_MAE, Cross_Max]
			best_cross_score = Cross_Overall
			CrossHistory = results
		if args["visualize"]:showBMIGraphs(history,Y_Classic,Y_test,Y_Cross_Val,x, directory, results)

	return bestscores, fold_string