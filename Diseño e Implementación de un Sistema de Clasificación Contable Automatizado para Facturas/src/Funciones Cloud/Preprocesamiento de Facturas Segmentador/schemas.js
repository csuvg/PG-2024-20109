/**
 * @author { Juan Carlos Bajan }
 * @copyright ARO Copyright 2023-2024
 * @license GPL
 * @modified Juan Carlos Bajan
 * @version 2.0.0
 * @status Develop
 *
 * @title Schemas
 * @description Script that checks if the handle data has all the neccessary attributes.
 */

const Joi = require('joi');

const reqScheme = Joi.object({
    company_id: Joi.string().required(),
	position: Joi.string().valid(
		'in', 
		'out'
	).required(),
});

module.exports = {
    reqScheme,
};