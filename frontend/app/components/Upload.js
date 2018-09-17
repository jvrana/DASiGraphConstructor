import React from 'react';
import FileInput from 'react-file-input';

class UploadForm extends React.Component {
    handleChange(event) {
        console.log('Selected file:', event.target.files[0]);
    }

    render() {
        return (
            <form>
                <FileInput name="myImage"
                           accept=".png,.gif"
                           placeholder="My Image"
                           className="inputClass"
                           onChange={this.handleChange}/>
            </form>
        );
    }
};

export default UploadForm;