import React from 'react';
import {Alert} from "react-bootstrap";

const NoServer = () => {
    return <Alert bsStyle="danger">
        Cannot continue. Backend server is not running!
    </Alert>;
}

export default NoServer;