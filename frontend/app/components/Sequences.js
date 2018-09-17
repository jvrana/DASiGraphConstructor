import React from 'react';
import {Query} from 'react-apollo';
import gql from 'graphql-tag';
import {ListGroup, ListGroupItem, Panel} from 'react-bootstrap';
import {Error, Loading} from './Loading';
import {BootstrapTable, TableHeaderColumn} from 'react-bootstrap-table';
import { sortBy, remove } from 'lodash';


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

// const Sequences = () => (
//     <Panel>
//         <Panel.Heading>Sequences</Panel.Heading>
//         <Panel.Body>
//             <ButtonToolbar>
//                 <AlignmentButton />
//             </ButtonToolbar>
//                             <UploadForm />
//             <Query query={GET_SEQUENCES}>
//                 {({loading, error, data}) => {
//                     if (loading) return <Loading msg={"Loading sequences..."}/>;
//                     if (error) return <Error err={error}/>;
//
//
//                     return <ListGroup>
//                         {data.sequences.map((d) => {
//                             return <Link to={`sequences/${d.id}`}>
//                                 <ListGroupItem>{d.name}</ListGroupItem>
//                             </Link>
//                         })
//                         }
//                     </ListGroup>
//                 }}
//             </Query>
//             <Route exact path="/sequences/:id" component={Sequence} />
//         </Panel.Body>
//     </Panel>
// );
//
// const GET_SEQUENCE = gql`
// {
//   node(id: "U2VxdWVuY2VzOjI=") {
//     __typename
//     ... on Sequences {
//       name
//       circular
//       bases
//       size
//       description
//     }
//   }
// }
// `;
//
// function Sequence({match}) {
//     return <Query query={GET_SEQUENCE} variables={match.params.id}>
//         {({loading, error, data}) => {
//             if (loading) return <Loading msg={"Loading sequence..."}/>;
//             if (error) return <Error err={error}/>;
//             console.log(data)
//             return <div>
//                 {data}
//                     </div>
//         }}
//     </Query>
// }

class SequenceEntry extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            sequence: props.sequence,
            toggle: false
        };
    }

    render() {
        return <ListGroupItem>
            {this.state.sequence.name}
        </ListGroupItem>
    }
}

class SequenceTable extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            sequences: props.sequences,
            selected: []
        };
        this.onRowSelect = this.onRowSelect.bind(this);
        console.log(props)
    }

    onRowSelect(row, isSelected, e) {
        let selected = this.state.selected;

        let pos = selected.indexOf(row.id);
        if (pos == -1) {
            selected.push(row.id);
        } else {
            console.log("removing!");
            remove(selected, (x) => {return x === row.id});
        }

        this.setState({
            selected: selected,
            sequences: sortBy(this.state.sequences, [(x) => {return selected.indexOf(x)}])
        });
        console.log(this.state.selected);
    }

    render() {
        console.log("Rendering");
        const selectRowProp = {
            mode: 'checkbox',
            bgColor: 'lightgreen', // you should give a bgcolor, otherwise, you can't regonize which row has been selected
            hideSelectColumn: true,  // enable hide selection column.
            clickToSelect: true,  // you should enable clickToSelect, otherwise, you can't select column.
            onSelect: this.onRowSelect,
        };
        return (
            <BootstrapTable data={this.state.sequences} selectRow={selectRowProp}>
                <TableHeaderColumn dataField='id' isKey>ID</TableHeaderColumn>
                <TableHeaderColumn dataField='name'>Name</TableHeaderColumn>
                <TableHeaderColumn dataField='size'>Length (bp)</TableHeaderColumn>
                <TableHeaderColumn dataField='circular'>Circular?</TableHeaderColumn>
            </BootstrapTable>
        );
    }
}

// class SequenceViewer extends React.Component {
//     constructor(props) {
//         super(props);
//
//
//         this.state = {
//             selected: [],
//             sequences: props.sequences
//         };
//         this.handleClick = this.handleClick.bind(this);
//     }
//
//     handleClick(seq) {
//         let selected = this.state.selected;
//         let pos = selected.indexOf(seq.id);
//         if (pos == -1) {
//             selected.push(seq.id);
//         } else {
//             selected.splice(pos, 1);
//         }
//         this.setState({
//             selected: selected
//         });
//         console.log("Selected " + seq.id);
//     }
//
//     render() {
//         console.log("Rendering...");
//         let selected = [];
//         let unselected = [];
//         this.state.sequences.forEach((s) => {
//             let pos = this.state.selected.indexOf(s.id);
//             if (pos == -1) {
//                 unselected.push(s);
//             } else {
//                 console.log(s.id + " is selected!");
//                 selected.push(s);
//             }
//         });
//         return <div>
//             <Panel>
//                 <Panel.Heading>Queries</Panel.Heading>
//                 <Panel.Body>
//                     <ListGroup>
//                         {selected.map((d) => {
//                             return <ListGroupItem onClick={() => {
//                                 return this.handleClick(d)
//                             }}>
//                                 {d.name}
//                             </ListGroupItem>
//                         })}
//                     </ListGroup>
//                 </Panel.Body>
//                 <Panel.Heading>Templates</Panel.Heading>
//                 <Panel.Body>
//                     <BootstrapTable data={unselected}>
//                         <TableHeaderColumn isKey={true} dataField={'id'}>ID</TableHeaderColumn>
//                         <TableHeaderColumn dataField={'name'}>Name</TableHeaderColumn>
//                         <TableHeaderColumn dataField={'circular'}>Circular</TableHeaderColumn>
//                         <TableHeaderColumn dataField={'size'}>Length (bp)</TableHeaderColumn>
//                     </BootstrapTable>
//                     <ListGroup>
//                         {unselected.map((d) => {
//                             return <ListGroupItem onClick={() => {
//                                 return this.handleClick(d)
//                             }}>
//                                 {d.name}
//                             </ListGroupItem>
//                         })}
//                     </ListGroup>
//                 </Panel.Body>
//             </Panel></div>
//     }
// }

const Sequences = () => {
    return <Query query={GET_SEQUENCES}>
        {({loading, error, data}) => {
            console.log("Performing query");
            if (loading) return <Loading msg={"Loading sequences..."}/>;
            if (error) return <Error err={error}/>;
            console.log("Rendering Sequence Viewer");
            return <SequenceTable sequences={data.sequences}/>
        }}
    </Query>
};


export default Sequences;