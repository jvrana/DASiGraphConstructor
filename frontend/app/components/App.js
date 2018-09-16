import React from 'react'
import {Alert } from 'react-bootstrap';
import {Helmet} from 'react-helmet';
import NavigationBar from './Nav'
import {COPYRIGHT, SITE_NAME} from './../config'

const AppLayout = () => {
    return <div>
        <Helmet titleTemplate={`%s - ${SITE_NAME}`}
                defaultTitle={SITE_NAME}/>
        <NavigationBar/>
        <Alert bsStyle="warning">
            <strong>Holy guacamole!</strong> Best check yo self, you're not looking too
            good.
        </Alert>;
        <footer className="center">
            Copyright {new Date().getFullYear()} {COPYRIGHT}
        </footer>
    </div>
};

export default (props) => (
    <AppLayout/>
)