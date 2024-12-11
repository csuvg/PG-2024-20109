const { distributeInvoices } = require('./controllers');
const { reqScheme } = require('./schemas');
const { initializeFirestoreClient } = require('./gcp-connections');

exports.invoice_preprocessing_notificator = async (req, res) => {
	// Setup CORS Headers
	const isPreflight = verifyCors(req, res);
	if (isPreflight) return;
	
	// Get Body
	const body = req.body;

	// Validate Schema
	const validateSchema = reqScheme.validate(body);
	if (validateSchema.error) {
		return res.status(400).send(validateSchema.error.details[0].message);
	}

	const { company_id, position } = body;

	await initializeFirestoreClient("default")

	const company = await verifyCompany(company_id, res);

	if (company == null) return;

	const result = distributeInvoices(company, position, user.path);

	if (!result) return res.status(500).send("Error starting Invoice datasets creation.")
	return res.status(200).send("Invoice datasets creation started.")

}