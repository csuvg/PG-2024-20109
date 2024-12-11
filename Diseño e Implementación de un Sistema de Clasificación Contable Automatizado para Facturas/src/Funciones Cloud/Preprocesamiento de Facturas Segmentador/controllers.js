const { getFirestore, pubsub } = require('./gcp-connections');
//require('dotenv').config();

const topicName = process.env.INVOICES_PREPROCESSING_TOPIC;
const BATCH_SIZE = 250;

async function distributeInvoices(company, position, path) {
    try {
        const invoicesQuery = getFirestore().collection('invoices')
            .where(position === 'in' ? 'sender_id' : 'receptor_id', '==', company.tid)
            .where(`accounting_specifications.${position}.state`, '==', 'verified')
            .orderBy('__name__');

        let lastVisible = null;
        let continueQuery = true;
        let batchId = 0;

        while (continueQuery) {
            let query = invoicesQuery.limit(BATCH_SIZE);
            if (lastVisible) {
                query = query.startAfter(lastVisible);
            }

            const snapshot = await query.get();
            if (snapshot.empty) {
                continueQuery = false;
                break;
            }

            const invoiceIds = snapshot.docs.map(doc => doc.id);
            await pubsub.topic(topicName).publish(Buffer.from(JSON.stringify({ company_id: company.id, position, invoiceIds, batchId, path })));

            lastVisible = snapshot.docs[snapshot.docs.length - 1];
            batchId += 1;
        }
        return true
    } catch (error) {
        console.error('Error distributing invoices:', error);
        // Retry logic or error handling can be added here
        return false
    }
}

exports.distributeInvoices = distributeInvoices;
