/**
 * @author { Juan Carlos Bajan }
 * @copyright ARO Copyright 2023-2024
 * @license GPL
 * @modified Cristian Laynez
 * @version 2.0.0
 * @status Production
 *
 * @title GCP Connections
 * @description In this code exists instances for access to the multiple libraries.
 * @augments {req, res}
 */

// require('dotenv').config(); // ! FOR LOCAL TESTING

const {Firestore} = require('@google-cloud/firestore');
const {GoogleAuth} = require('google-auth-library');
const {PubSub} = require('@google-cloud/pubsub');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');
const secretManagerClient = new SecretManagerServiceClient();
const pubsub = new PubSub();
const auth = new GoogleAuth();
let firestore = null;

async function initializeFirestoreClient(databaseId) {
    firestore = new Firestore({
        databaseId: databaseId,
    });
}

const getFirestore = () => {
    return firestore
}

async function getSecretFromManager(secretName) {
    const projectId = process.env.PROJECT_ID;
    const secretVersion = 'latest'; // o un número de versión específico
  
    const name = `projects/${projectId}/secrets/${secretName}/versions/${secretVersion}`;
  
    try {
      const [version] = await secretManagerClient.accessSecretVersion({ name });
      const payload = version.payload.data.toString('utf8');
      return payload;
    } catch (error) {
      console.error(`Failed to access secret: ${error.message}`);
    }
  }

module.exports = {
    auth, 
    pubsub,
    fetch,
    firestore,
    getFirestore,
    getSecretFromManager,
    initializeFirestoreClient
}