import React from 'react';
import {ControlLabel, FormControl, FormGroup, HelpBlock, Button} from 'react-bootstrap';

function FieldGroup({id, label, help, type}) {
    return (
        <FormGroup controlId={id}>
            <ControlLabel>{label}</ControlLabel>
            <FormControl type={type}/>
            {help && <HelpBlock>{help}</HelpBlock>}
        </FormGroup>
    );
}


class UploadForm extends React.Component {
    constructor() {
        super();
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(event) {
        event.preventDefault();
        const data = new FormData(event.target);

        // do something
        console.log("Form submitted!");
        console.log(data);
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <FormGroup controlId="formControlsFile">
                    <ControlLabel>Upload Query</ControlLabel>
                    <FormControl type="file"/>
                    <HelpBlock>Help block text</HelpBlock>
                </FormGroup>
                <Button type="submit">Submit</Button>
            </form>
        )
    }
}

export default UploadForm;