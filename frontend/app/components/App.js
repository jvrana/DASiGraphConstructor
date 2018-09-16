import React from 'react'
import {Helmet} from 'react-helmet';
import NavigationBar from './Nav'
import {COPYRIGHT, SITE_NAME} from './../config'
import {BrowserRouter, Route, Switch} from "react-router-dom";

import Home from "./Home";
import NoServer from "./NoServer";
import Sequences from "./Sequences";

const AppLayout = () => {
    return <BrowserRouter>
        <div>
            <Helmet titleTemplate={`%s - ${SITE_NAME}`}
                    defaultTitle={SITE_NAME}/>
            <NavigationBar/>
            <main>
                <Switch>
                    <Route exact path="/" component={Home}/>
                    <Route exact path="/noserver" component={NoServer}/>
                    <Route exact path="/sequences" component={Sequences}/>
                </Switch>
            </main>
            <footer className="center">
                Copyright {new Date().getFullYear()} {COPYRIGHT}
            </footer>
        </div>
    </BrowserRouter>
};

export default (props) => (
    <AppLayout/>
)