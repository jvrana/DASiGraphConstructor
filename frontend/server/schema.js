const anyToJson = require('bio-parsers').anyToJson;
const jsonToGenbank = require('bio-parsers').jsonToGenbank;
const jsonToFasta = require('bio-parsers').jsonToFasta;
const makeExecutableSchema = require('graphql-tools').makeExecutableSchema;

const typeDefs = `
  scalar JSON
  type Query {
    tojson(file: String!, filename: String!): Result,
    tojsons(files: [String!], filenames: [String!]): [Result],
    tofasta(json: SequenceInput!): String
    togenbank(json: SequenceInput!): String
  }
  
  input Lat {
    lat: Float,
    lon: Float,
    }
    
  
  type Result {
    messages: [String],
    success: Boolean,
    parsedSequence: Sequence
  }

  type Feature {
        name: String!,
        type: String,
        id: ID,
        start: Int!,
        end: Int!
        strand: Int!
  }
 
  type Sequence {
        size: Int,
        sequence: String!,
        circular: Boolean,
        name: String!,
        id: ID,
        description: String,
        features: [Feature!]
  }
  
  input SequenceInput {
    sequence: String!,
    circular: Boolean,
    name: String!,
    description: String,
    features: [FeatureInput!]
  }
  
  input FeatureInput {
         name: String!,
        type: String,
        id: ID,
        start: Int!,
        end: Int!
        strand: Int!
  }
`;

// Provide resolver functions for your schema fields
const resolvers = {
    Query: {
        tojson: async (root, {file, filename}, context) => {
            const response = await anyToJson(file, {"fileName": filename});
            return response[0]
        },
        tojsons: async (root, {files, filenames}, context) => {
            const promises = files.map((f, i) => {
                return anyToJson(f, filenames[i])
            });
            let res = await Promise.all(promises);
            res = res.map((x) => x[0]);
            return res
        },
        tofasta: async (root, { data }, context) => {
            const response = await jsonToFasta(data);
            return response
        },
        togenbank: async (root, { data }, context) => {
            const response = await jsonToGenbank(data);
            return response
        },
    },
};

const schema = makeExecutableSchema({
    typeDefs,
    resolvers,
});

module.exports = schema;