#-----------------------------------------
#-----------------------------------------
#  This projects uses the SciPy, NumPy, Lmfit-py, and Flask projects to operate
#-----------------------------------------
#-----------------------------------------
#
#  The SciPy code is distribution under the following license:
#
#  Copyright (c) 2001, 2002 Enthought, Inc.
#  All rights reserved.
#
#  Copyright (c) 2003-2016 SciPy Developers.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  a. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#  b. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  c. Neither the name of Enthought nor the names of the SciPy Developers
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS
#  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
#  OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
#  THE POSSIBILITY OF SUCH DAMAGE.
#
#-----------------------------------------
#
#  The NumPy code is distribution under the following license:
#
#  Copyright (c) 2005-2016, NumPy Developers.
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification, 
#  are permitted provided that the following conditions are met:
#  
#  *  Redistributions of source code must retain the above copyright notice, this list 
#  of conditions and the following disclaimer.
#  
#  *  Redistributions in binary form must reproduce the above copyright notice, this 
#  list of conditions and the following disclaimer in the documentation and/or other 
#  materials provided with the distribution.
#  
#  *  Neither the name of the NumPy Developers nor the names of any contributors may be 
#  used to endorse or promote products derived from this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
#  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
#  THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
#  GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND 
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
#  POSSIBILITY OF SUCH DAMAGE.
#  
#-----------------------------------------
#
#  The LMFIT-py code is distribution under the following license:
#
#  Copyright (c) 2014 Matthew Newville, The University of Chicago
#                     Till Stensitzki, Freie Universitat Berlin
#                     Daniel B. Allen, Johns Hopkins University
#                     Michal Rawlik, Eidgenossische Technische Hochschule, Zurich
#                     Antonino Ingargiola, University of California, Los Angeles
#                     A. R. J. Nelson, Australian Nuclear Science and Technology Organisation
#
#  Permission to use and redistribute the source code or binary forms of this
#  software and its documentation, with or without modification is hereby
#  granted provided that the above notice of copyright, these terms of use,
#  and the disclaimer of warranty below appear in the source code and
#  documentation, and that none of the names of above institutions or
#  authors appear in advertising or endorsement of works derived from this
#  software without specific prior written permission from all parties.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THIS SOFTWARE.
#
#-----------------------------------------
#
#  The Flask code is distribution under the following license:
#
#  Copyright (c) 2015 by Armin Ronacher and contributors. See AUTHORS for more details.
#  
#  Some rights reserved.
#  
#  Redistribution and use in source and binary forms of the software as well as documentation, 
#  with or without modification, are permitted provided that the following conditions are met:
#  
#  *  Redistributions of source code must retain the above copyright notice, this list of conditions 
#  and the following disclaimer.
#  
#  *  Redistributions in binary form must reproduce the above copyright notice, this list of conditions 
#  and the following disclaimer in the documentation and/or other materials provided with the distribution.
#  
#  *  The names of the contributors may not be used to endorse or promote products derived from this 
#  software without specific prior written permission.
#  
#  THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING 
#  IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from flask import Flask, render_template, json, request, jsonify
from lmfit import minimize, Parameters
import numpy as np
import matplotlib.pyplot as plt
import StringIO
import base64
import string
import random

app = Flask(__name__)
session_objs = {}
model_bic = {}
legend = []
method = 'leastsq'

# Create comma separated string from array, for JSON response
def GetCSV(array):
	arrstr = np.char.mod('%f', array)
	return ",".join(arrstr)

# Lmfit Module
def NoiseResidual(params, x, y):
	'Noise Model'
	model = 1
	return y - model

# Lmfit Module
def ExponentialResidual(params, x, y):
	'Exponential Residual Model'
	k = params['k']
	model = 1 * np.exp(-k * x)
	return y - model

# Lmfit Module
def HyperbolicResidual(params, x, y):
	'Hyperbolic Residual Model'
	k = params['k']
	model = 1.0/(1 + k * x)
	return y - model

# Lmfit Module
def QuasiHyperbolicResidual(params, x, y):
	'Quasi Hyperbolic Residual Model'
	b = params['b']
	d = params['d']	
	model = 1.0 * b * np.exp(-d * x)
	return y - model

# Lmfit Module
def MyersonResidual(params, x, y):
	'Myerson Residual Model'
	k = params['k']
	s = params['s']	
	model = 1.0 / np.power((1 + k * x), s)
	return y - model

# Lmfit Module
def RachlinResidual(params, x, y):
	'Myerson Residual Model'
	k = params['k']
	s = params['s']	
	model = 1.0 / (1 + np.power((k * x), s))   
	return y - model

# Plotting Module
def ExponentialFunction(x, a):
    'Exponential Decay'
    return 1.0 * np.exp(-a * x)

# Plotting Module
def HyperbolicFunction(x, a):
    'Hyperbolic Decay'
    return 1.0/(1 + a * x)

# Plotting Module
def QuasiHyperbolicFunction(x, b, d):
    'Quasi Hyperbolic Decay'
    return 1.0 * b * np.exp(-d * x)

# Plotting Module
def MyersonHyperbolicFunction(x, k, s):
    'Myerson Decay'
    return 1.0/np.power((1 + k * x), s)

# Plotting Module
def RachlinHyperbolicFunction(x, k, s):
    'Rachlin Decay'
    return 1.0/(1 + np.power((k * x), s))    

# Plotting Module
def TokenMethod(size=64, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

# Flask Routing
@app.route("/")
def main():
	session_objs['csrf'] = TokenMethod()	
	return render_template('index.html', csrf_token=session_objs['csrf'])

# Flask Routing
@app.route('/scoreValues', methods=['POST'])
def scoreValues():
	# read the posted values from the UI
	_x = request.json['inputX']
	_y = request.json['inputY']
	_a = request.json['inputA']
	_opt = request.json['rachlinBound']
	_csrf = request.json['csrf']
	_figNormal = request.json['showNormal']
	_figLogged = request.json['showLogged']
	_selection = request.json['showProbs']
	_figProbs = request.json['modelSelection']

	returns = {}
	returns["Messages"] = "Passed";	
	returns["FigNormalFlag"] = _figNormal
	returns["FigLoggedFlag"] = _figLogged
	returns["FigProbs"] = _figProbs
	returns["ModelSelection"] = _selection

	if _csrf != session_objs['csrf']:
		returns["Messages"] = "Error";	
		return json.dumps(returns, ensure_ascii=False);

	if _x and _y and _a:
		x = np.fromstring(_x, dtype=float, sep=',')
		y = np.fromstring(_y, dtype=float, sep=',')

		plt.clf()
		plt.cla()
		plt.plot(x,y,'bo')
		xfit = np.linspace(0,x.max())

		legend = []
		legend.append("Indifference Points")

		try: #Noise
			noiseParams = Parameters()
			noiseResult = minimize(NoiseResidual,
				noiseParams,
				args=(x,y),
				nan_policy='propagate')
			returns["NoiseAIC"] = noiseResult.aic			
			returns["NoiseBIC"] = noiseResult.bic

			model_bic["Noise"] = noiseResult.bic
		except Exception, e:
			returns["Noise"] = str(e)
			returns["NoiseAIC"] = ""
			returns["NoiseBIC"] = ""			

		try: #Exponential
			expParams = Parameters()
			expParams.add('k', value=0.001)
			expResult = minimize(ExponentialResidual, 
				expParams, 
				args=(x, y), 
				nan_policy='propagate', 
				method=method)

			returns["Exponential"] = expResult.params['k'].value
			returns["ExponentialLower"] = expResult.params['k'].value - expResult.params['k'].stderr
			returns["ExponentialUpper"] = expResult.params['k'].value + expResult.params['k'].stderr
			returns["ExponentialResid"] = GetCSV(expResult.residual)
			returns["ExponentialAIC"] = expResult.aic
			returns["ExponentialBIC"] = expResult.bic

			model_bic["Exponential"] = expResult.bic			

			expFit = ExponentialFunction(xfit, expResult.params['k'].value)
			plt.plot(xfit,expFit,'black')

			legend.append("Exponential")

		except Exception, e:
			returns["Exponential"] = str(e)
			returns["ExponentialLower"] = ""
			returns["ExponentialUpper"] = ""

		try: #Hyperbolic
			hypParams = Parameters()
			hypParams.add('k', value=0.001)
			hypResult = minimize(HyperbolicResidual, hypParams, args=(x, y), nan_policy='propagate', method=method)

			returns["Hyperbolic"] = hypResult.params['k'].value
			returns["HyperbolicLower"] = hypResult.params['k'].value - hypResult.params['k'].stderr
			returns["HyperbolicUpper"] = hypResult.params['k'].value + hypResult.params['k'].stderr
			returns["HyperbolicResid"] = GetCSV(hypResult.residual)
			returns["HyperbolicAIC"] = hypResult.aic
			returns["HyperbolicBIC"] = hypResult.bic		

			model_bic["Hyperbolic"] = hypResult.bic		

			hypFit = HyperbolicFunction(xfit, hypResult.params['k'].value)
			plt.plot(xfit,hypFit,'blue')

			legend.append("Hyperbolic")			

		except Exception, e:
			returns["Hyperbolic"] = str(e)
			returns["HyperbolicLower"] = ""
			returns["HyperbolicUpper"] = ""	

		try: #BetaDelta
			qHypParams = Parameters()
			qHypParams.add('b', value=0.001, min=0.0, max=1.0)
			qHypParams.add('d', value=0.001, min=0.0, max=1.0)
			qHypResult = minimize(QuasiHyperbolicResidual, qHypParams, args=(x, y), nan_policy='propagate', method=method)

			returns["QuasiHyperbolicBeta"] = qHypResult.params['b'].value
			returns["QuasiHyperbolicBetaLower"] = qHypResult.params['b'].value - qHypResult.params['b'].stderr
			returns["QuasiHyperbolicBetaUpper"] = qHypResult.params['b'].value + qHypResult.params['b'].stderr

			returns["QuasiHyperbolicDelta"] = qHypResult.params['d'].value
			returns["QuasiHyperbolicDeltaLower"] = qHypResult.params['d'].value - qHypResult.params['d'].stderr
			returns["QuasiHyperbolicDeltaUpper"] = qHypResult.params['d'].value + qHypResult.params['d'].stderr			

			returns["QuasiHyperbolicAIC"] = qHypResult.aic
			returns["QuasiHyperbolicBIC"] = qHypResult.bic			

			model_bic["QuasiHyperbolic"] = qHypResult.bic		

			returns["QuasiHyperbolicResid"] = GetCSV(qHypResult.residual)

			qHypFit = QuasiHyperbolicFunction(xfit, qHypResult.params['b'].value, qHypResult.params['d'].value)
			plt.plot(xfit,qHypFit,'red')

			legend.append("QuasiHyperbolic")

		except Exception, e:
			returns["QuasiHyperbolicBeta"] = str(e)
			returns["QuasiHyperbolicBetaLower"] = ""
			returns["QuasiHyperbolicBetaUpper"] = ""	

			returns["QuasiHyperbolicDelta"] = ""
			returns["QuasiHyperbolicDeltaLower"] = ""
			returns["QuasiHyperbolicDeltaUpper"] = ""	

		try: #Myerson
			myerParams = Parameters()
			myerParams.add('k', value=0.001)
			myerParams.add('s', value=0.001)
			myerResult = minimize(MyersonResidual, myerParams, args=(x, y), nan_policy='propagate', method=method)

			returns["MyersonK"] = myerResult.params['k'].value
			returns["MyersonKLower"] = myerResult.params['k'].value - myerResult.params['k'].stderr
			returns["MyersonKUpper"] = myerResult.params['k'].value + myerResult.params['k'].stderr

			returns["MyersonS"] = myerResult.params['s'].value
			returns["MyersonSLower"] = myerResult.params['s'].value - myerResult.params['s'].stderr
			returns["MyersonSUpper"] = myerResult.params['s'].value + myerResult.params['s'].stderr			

			returns["MyersonAIC"] = myerResult.aic
			returns["MyersonBIC"] = myerResult.bic	

			model_bic["Myerson"] = myerResult.bic	

			returns["MyersonResid"] = GetCSV(myerResult.residual)			

			myerFit = MyersonHyperbolicFunction(xfit, myerResult.params['k'].value, myerResult.params['s'].value)
			plt.plot(xfit,myerFit,'green')

			legend.append("Myerson")

		except Exception, e:
			returns["MyersonK"] = str(e)
			returns["MyersonKLower"] = ""
			returns["MyersonKUpper"] = ""

			returns["MyersonS"] = ""
			returns["MyersonSLower"] = ""
			returns["MyersonSUpper"] = ""

		try: #Rachlin

			rachParams = Parameters()
			rachParams.add('k', value=0.001)

			if str(_opt) is "true":
				rachParams.add('s', value=0.001, min=0.0, max=1.0)
			else:
				rachParams.add('s', value=0.001)

			rachResult = minimize(RachlinResidual, rachParams, args=(x, y), nan_policy='propagate', method=method)

			returns["RachlinK"] = rachResult.params['k'].value
			returns["RachlinKLower"] = rachResult.params['k'].value - rachResult.params['k'].stderr
			returns["RachlinKUpper"] = rachResult.params['k'].value + rachResult.params['k'].stderr

			returns["RachlinS"] = rachResult.params['s'].value
			returns["RachlinSLower"] = rachResult.params['s'].value - rachResult.params['s'].stderr
			returns["RachlinSUpper"] = rachResult.params['s'].value + rachResult.params['s'].stderr		

			returns["RachlinAIC"] = rachResult.aic
			returns["RachlinBIC"] = rachResult.bic		

			model_bic["Rachlin"] = rachResult.bic					

			returns["RachlinResid"] = GetCSV(rachResult.residual)

			rachFit = RachlinHyperbolicFunction(xfit, rachResult.params['k'].value, rachResult.params['s'].value)
			plt.plot(xfit,rachFit,'purple')

			legend.append("Rachlin")
			
		except Exception, e:
			returns["RachlinK"] = str(e)
			returns["RachlinKLower"] = ""
			returns["RachlinKUpper"] = ""

			returns["RachlinS"] = ""
			returns["RachlinSLower"] = ""
			returns["RachlinSUpper"] = ""		

		plt.legend(legend, loc='best')

		if _figNormal:
			plt.title('Discounting Functions')
			plt.ylabel('Value')
			plt.xlabel('Delay')
			imgdata = StringIO.StringIO()
			plt.savefig(imgdata, format='png')
			imgdata.seek(0)  # rewind the data
			returns["Plot"] = base64.b64encode(imgdata.buf)
		else:
			returns["Plot"] = str(_figNormal)

		if _figLogged:
			plt.title('Discounting Functions, ln(Delays)')
			plt.ylabel('Value')			
			plt.xlabel('ln(Delay)')
			plt.xscale('log')
			imgdataLog = StringIO.StringIO()
			plt.savefig(imgdataLog, format='png')
			imgdataLog.seek(0)  # rewind the data		
			returns["PlotLog"] = base64.b64encode(imgdataLog.buf)
		else:
			returns["PlotLog"] = str(_figLogged)

		if _figProbs:

			sum_scaled_bic = 0

			for key, value in model_bic.iteritems():
				value = -np.exp(-0.5 * (value - model_bic["Noise"]))

			for key, value in model_bic.iteritems():
				sum_scaled_bic = sum_scaled_bic + value

			returns["SumScaledBIC"] = sum_scaled_bic

			for key, value in model_bic.iteritems():
				value = value/sum_scaled_bic
				save_key = key + "Probs"
				returns[save_key] = value			

			plt.clf()
			plt.cla()

			labels = ["Noise", "Exponential", "Hyperbolic", "BetaDelta", "Myerson", "Rachlin"]
			values = [returns["NoiseProbs"],returns["ExponentialProbs"],returns["HyperbolicProbs"],returns["QuasiHyperbolicProbs"],returns["MyersonProbs"],returns["RachlinProbs"]]
			ticks = [1,2,3,4,5,6]

			plt.bar(ticks, values, align='center')
			plt.xticks(ticks, labels)			
			plt.title('Model Probabilities')
			plt.ylabel('Probability')			
			plt.xlabel('Model')
			plt.tick_params(axis='x', which='major', labelsize=10)
			imgdataLog = StringIO.StringIO()
			plt.savefig(imgdataLog, format='png')
			imgdataLog.seek(0)  # rewind the data		
			returns["PlotProb"] = base64.b64encode(imgdataLog.buf)
		elif _selection:

			sum_scaled_bic = 0

			for key, value in model_bic.iteritems():
				value = -np.exp(-0.5 * (value - model_bic["Noise"]))

			for key, value in model_bic.iteritems():
				sum_scaled_bic = sum_scaled_bic + value

			returns["SumScaledBIC"] = sum_scaled_bic

			for key, value in model_bic.iteritems():
				value = value/sum_scaled_bic
				save_key = key + "Probs"
				returns[save_key] = value

			returns["PlotProb"] = "False"
		else:
			returns["PlotProb"] = "False"

		return json.dumps(returns, ensure_ascii=False);

	else:
		returns["Messages"] = "Failed";	
		return json.dumps(returns, ensure_ascii=False);

if __name__ == "__main__":
	app.run()
