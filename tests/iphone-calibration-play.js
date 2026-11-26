/* Actual phone DOM activation, NOT a trusted finger/user-activation claim. */
(()=>{const $=id=>document.getElementById(id);if($('calibrationPanel').hidden||$('calibrationPlay').disabled)throw Error('Calibration not ready');$('calibrationPlay').click();return{oneSyntheticCalibrationPlay:true};})()
