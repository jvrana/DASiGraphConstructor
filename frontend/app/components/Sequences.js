import React from 'react';
import {Query} from 'react-apollo';
import gql from 'graphql-tag';
import { Link, Route } from 'react-router-dom';
import {ListGroup, ListGroupItem, Panel, ButtonToolbar, Button} from 'react-bootstrap';
import { Error, Loading } from './Loading';
import AlignmentButton from './AlignmentButton';
import UploadForm from './Upload';
export const GET_SEQUENCES = gql`
{
  sequences {
    id
    circular
    bases
    size
    name
  }
}
`;

const Sequences = () => (
    <Panel>
        <Panel.Heading>Sequences</Panel.Heading>
        <Panel.Body>
            <ButtonToolbar>
                <AlignmentButton />
            </ButtonToolbar>
             <UploadForm />
            <Query query={GET_SEQUENCES}>
                {({loading, error, data}) => {
                    if (loading) return <Loading msg={"Loading sequences..."}/>;
                    if (error) return <Error err={error}/>;


                    return <ListGroup>
                        {data.sequences.map((d) => {
                            return <Link to={`sequences/${d.id}`}>
                                <ListGroupItem>{d.name}</ListGroupItem>
                            </Link>
                        })
                        }
                    </ListGroup>
                }}
            </Query>
            <Route exact path="/sequences/:id" component={Sequence} />
        </Panel.Body>
    </Panel>
);

const GET_SEQUENCE = gql`
{
  node(id: "U2VxdWVuY2VzOjI=") {
    __typename
    ... on Sequences {
      name
      circular
      bases
      size
      description
    }
  }
}
`;

function Sequence({match}) {
    return <Query query={GET_SEQUENCE} variables={match.params.id}>
        {({loading, error, data}) => {
            if (loading) return <Loading msg={"Loading sequence..."}/>;
            if (error) return <Error err={error}/>;
            console.log(data)
            return <div>
                {data}
                    </div>
        }}
    </Query>
}

export default Sequences;