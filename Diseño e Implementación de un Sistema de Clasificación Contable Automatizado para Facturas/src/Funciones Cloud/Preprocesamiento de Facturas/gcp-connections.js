const {Firestore} = require('@google-cloud/firestore');
const {Storage} = require('@google-cloud/storage');

const firestore = new Firestore();
const storage = new Storage();

const getFirestore = (databaseId) => {
    return new Firestore({
        databaseId
    })
}

module.exports = {
    firestore,
    storage,
    getFirestore
}
