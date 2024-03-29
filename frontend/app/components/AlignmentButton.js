import React from 'react'
import { Button } from 'react-bootstrap';




class AlignmentButton extends React.Component {
  constructor(props, context) {
    super(props, context);

    this.handleClick = this.handleClick.bind(this);

    this.state = {
      isLoading: false
    };
  }

  handleClick() {
    this.setState({ isLoading: true });

    // This probably where you would have an `ajax` call
    setTimeout(() => {
      // Completed of async action, set loading state back
      this.setState({ isLoading: false });
    }, 2000);
  }

  render() {
    const { isLoading } = this.state;

    return (
      <Button
        bsStyle="primary"
        disabled={isLoading}
        onClick={!isLoading ? this.handleClick : null}
      >
        {isLoading ? 'Aligning...' : 'Align to sequences'}
      </Button>
    );
  }
}
export default AlignmentButton