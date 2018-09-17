import React from 'react';
import { Alert, ProgressBar } from 'react-bootstrap';

const Error = (err) => (
    <Alert bsStyle="danger">
        <strong>Error: </strong>{err}
    </Alert>
);

function Loading(props) {
    return <div>
        <strong>{props.msg}</strong>
         <ProgressBar active bsStyle="success" now={50} key={1}></ProgressBar>
    </div>
}

export { Error, Loading }