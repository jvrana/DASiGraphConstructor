import React, { Component } from 'react';

class Sequencese extends Component {
    constructor(props) {
        super(props);

        this.state = {
            data: null,
        };
    }

    componentDidMount() {
        fetch('/api/graphql')
    }
}