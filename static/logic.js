/*

Copyright 2016 Shawn Gilroy

This file is part of Python Discounting Web App.

Discounting Web App is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2.

Discounting Web App is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Discounting Web App.  If not, see http:# www.gnu.org/licenses/. 

The Discounting Web App is a tool to assist researchers in behavior economics 
and behavioral decision-making.

Email: shawn(dot)gilroy(at)temple.edu

-----------------------------------------

The Python Discounting Web App uses Handsontable and Bootstrap to function

-----------------------------------------

Handsontable Open Source Version

The MIT License

Last updated January 5th, 2016

Copyright (c) 2015 Handsoncode sp. z o.o. <hello@handsoncode.net>

Copyright (c) 2012-2014 Marcin Warpechowski

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the 'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the
following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

*/

var hot;

function Summary(paramName, paramValue, paramLower, paramUpper, absSS, aic, bic, prob) {
    var str = '';

    str += '<p>' +
        '<b>Results for ' + paramName + ': </b><br>' +
        'Estimate: ' + paramValue + '<br>' +
        'Lower bound (95% CI): ' + paramLower + '<br>' +
        'Upper bound (95% CI): ' + paramUpper + '<br>' +
        'Absolute Sum Squares: ' + absSS + '<br>' +
        'AIC: ' + aic + '<br>' +
        'BIC: ' + bic + '<br>';

    if (prob != null) {
        str += 'Model Probability: ' + prob + '<br>';        
    }

    str += '</p>';

    return str;
}

function SummaryTwo(paramName, paramValue, paramLower, paramUpper, paramName2, paramValue2, paramLower2, paramUpper2, absSS, aic, bic, prob) {
    var str = '';

    str += '<p>' +
        '<b>Results for ' + paramName + ': </b><br>' +
        'Estimate: ' + paramValue + '<br>' +
        'Lower bound (95% CI): ' + paramLower + '<br>' +
        'Upper bound (95% CI): ' + paramUpper + '<br>' +

        '<b>Results for ' + paramName2 + ': </b><br>' +
        'Estimate: ' + paramValue2 + '<br>' +
        'Lower bound (95% CI): ' + paramLower2 + '<br>' +
        'Upper bound (95% CI): ' + paramUpper2 + '<br>' +

        'Absolute Sum Squares: ' + absSS + '<br>' +
        'AIC: ' + aic + '<br>' +
        'BIC: ' + bic + '<br>';

        if (prob != null) {
            str += 'Model Probability: ' + prob + '<br>';        
        }

        str += '</p>';

    return str;
}

function GetAbsSumSquares(string) {

    if (string === "---") {
        return string;
    }

    var sum = 0.0;

    var items = string.split(',');

    for (var i=0; i < items.length; i++) {
        sum = sum + Math.pow(parseFloat(items[i]), 2);
    }

    return sum;
}

$(document).ready(function() {
    $('#testButton').on('click', function(event) {
        event.preventDefault();

        var data = hot.getData();

        var xArray = [];
        var yArray = [];

        for (var i = 0; i < data.length; i++) {
            var row = data[i];

            if ($.isNumeric(row[0]) && $.isNumeric(row[1])) {
                xArray.push(parseFloat(row[0]));
                yArray.push(parseFloat(row[1]));
            }
        }

        var data = new Object();
        data["inputX"] = xArray.join(",");
        data["inputY"] = yArray.join(",");
        data["inputA"] = 1;
        data["csrf"] = $("#csrf").html();
        data["rachlinBound"] = $("#boundRachlin").prop('checked');
        data["modelSelection"] = $("#modelSelection").prop('checked');
        data["showNormal"] =   $("#showFigure").prop('checked');
        data["showLogged"] =   $("#showFigureLog").prop('checked');
        data["showProbs"] =   $("#showFigureProbs").prop('checked');

        if (data["showProbs"]) {
            data["modelSelection"] = true;
        }

        $.ajax({
            type: "POST",
            url: "scoreValues",
            data: JSON.stringify(data, null, '\t'),
            contentType: 'application/json;charset=UTF-8',
            success: function(result) {
                var mJson = JSON.parse(result);

                console.log(mJson);

                if (mJson["Messages"] != "Passed") {
                    console.log(mJson);
                    return;
                }

                $("#img_preview").empty();
                $("#img_preview").append("<h4>Results of Analysis</h4>");
                $("#img_preview").append("<p>Results and any figures selected will appear below.");

                if ($("#showFigure").prop('checked')) {
                    $("<img>", {
                        "src": "data:image/png;base64," + mJson["Plot"],
                        "min-width": "90%",
                        "width": "90%",
                        "height": "auto"
                    }).appendTo("#img_preview");
                }

                if ($("#showFigureLog").prop('checked')) {
                    $("<img>", {
                        "src": "data:image/png;base64," + mJson["PlotLog"],
                        "min-width": "90%",
                        "width": "90%",
                        "height": "auto"
                    }).appendTo("#img_preview");
                }  

                if ($("#showFigureProbs").prop('checked')) {
                    $("<img>", {
                        "src": "data:image/png;base64," + mJson["PlotProb"],
                        "min-width": "90%",
                        "width": "90%",
                        "height": "auto"
                    }).appendTo("#img_preview");
                }                            

                $("#results").empty();
                $("#scrollBoxOutput").empty();

                var content = "";

                content += Summary("Noise Model", "---", "---", "---", 
                    GetAbsSumSquares("---"), mJson["NoiseAIC"], mJson["NoiseBIC"], mJson["NoiseProbs"]);
                
                content += Summary("Exponential (k)", mJson["Exponential"], mJson["ExponentialLower"], mJson["ExponentialUpper"], 
                    GetAbsSumSquares(mJson["ExponentialResid"]), mJson["ExponentialAIC"], mJson["ExponentialBIC"], mJson["ExponentialProbs"]);

                content += Summary("Hyperbolic (k)", mJson["Hyperbolic"], mJson["HyperbolicLower"], mJson["HyperbolicUpper"], 
                    GetAbsSumSquares(mJson["HyperbolicResid"]), mJson["HyperbolicAIC"], mJson["HyperbolicBIC"], mJson["HyperbolicProbs"]);

                content += SummaryTwo("QuasiHyperbolic (b)", mJson["QuasiHyperbolicBeta"], mJson["QuasiHyperbolicBetaLower"], mJson["QuasiHyperbolicBetaUpper"], 
                    "QuasiHyperbolic (d)", mJson["QuasiHyperbolicDelta"], mJson["QuasiHyperbolicDeltaLower"], mJson["QuasiHyperbolicDeltaUpper"],
                    GetAbsSumSquares(mJson["QuasiHyperbolicResid"]), mJson["QuasiHyperbolicAIC"], mJson["QuasiHyperbolicBIC"], mJson["QuasiHyperbolicProbs"]);

                content += SummaryTwo("Myerson (k)", mJson["MyersonK"], mJson["MyersonKLower"], mJson["MyersonKUpper"], 
                    "Myerson (s)", mJson["MyersonS"], mJson["MyersonSLower"], mJson["MyersonSUpper"], 
                    GetAbsSumSquares(mJson["MyersonResid"]), mJson["MyersonAIC"], mJson["MyersonBIC"], mJson["MyersonProbs"]);

                content += SummaryTwo("Rachlin (k)", mJson["RachlinK"], mJson["RachlinKLower"], mJson["RachlinKUpper"], 
                    "Rachlin (s)", mJson["RachlinS"], mJson["RachlinSLower"], mJson["RachlinSUpper"], 
                    GetAbsSumSquares(mJson["RachlinResid"]), mJson["RachlinAIC"], mJson["RachlinBIC"], mJson["RachlinProbs"]);
                
                content += "";

                //$('#results').append(content);
                $('#scrollBoxOutput').append(content);
            }
        });
    });

    var sheet = document.getElementById('sheet');

    var startData = [
        ["1", "1.0", ],
        ["30", "0.9", ],
        ["180", "0.85", ],
        ["540", "0.8", ],
        ["1080", "0.75", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ],
        ["", "", ]
    ];

    hot = new Handsontable(sheet, {
        data: startData,
        rowHeaders: true,
        colHeaders: ["Delays", "Values"],
        stretchH: "all",
        minSpareRows: 1,
        fixedRowsTop: 0,
        fixedColumnsLeft: 0
    });

});