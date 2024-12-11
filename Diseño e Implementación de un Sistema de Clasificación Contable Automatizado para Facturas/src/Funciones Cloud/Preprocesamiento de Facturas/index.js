const { processInvoices } = require("./controllers");

exports.invoice_preprocessing = async (message, context) => {
  try {
    // Decodificar el mensaje de Pub/Sub
    const dataBuffer = Buffer.from(message.data, 'base64');
    const data = JSON.parse(dataBuffer.toString());

    // Extraer los campos necesarios del mensaje
    const { company_id, position, invoiceIds, batchId, path } = data;

    // Procesar las facturas
    const result = await processInvoices(company_id, position, invoiceIds, batchId, path);

  } catch (error) {
    console.error('Error processing message:', error);
  }
};
