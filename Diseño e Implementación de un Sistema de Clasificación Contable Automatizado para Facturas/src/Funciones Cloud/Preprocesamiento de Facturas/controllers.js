const { storage, getFirestore } = require('./gcp-connections');
const { modifyInvoice } = require('./utils');

async function processInvoices(company_id, position, invoiceIds, batchId, path) {
    try {
        const bucket = storage.bucket(process.env.CLASSIFY_BUCKET_NAME);
        const firestore = getFirestore(path)
        const docRefs = invoiceIds.map(id => firestore.collection('invoices').doc(id));

        const docSnapshots = await firestore.getAll(...docRefs);
        const allItems = [];

        docSnapshots.forEach(docSnapshot => {
            if (!docSnapshot.exists) {
                return;
            }
            const invoiceData = docSnapshot.data();
            const modifiedInvoice = modifyInvoice(invoiceData, position);
            allItems.push(...modifiedInvoice);
        });


        if (allItems.length > 0) {
            const blob = bucket.file(`${path}/${company_id}/${position}/dataset/${batchId}.json`);
            const jsonData = JSON.stringify(allItems);
            await blob.save(jsonData, { resumable: false, contentType: 'application/json' });
        }
        return true
    } catch (error) {
        console.error('Error processing invoices:', error);
        return false
    }
}

exports.processInvoices = processInvoices;
