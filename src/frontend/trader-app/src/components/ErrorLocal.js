import * as React from 'react';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import Box from '@mui/material/Box';

class ErrorLocal extends React.Component {
    constructor(props) {
        super(props);
        this.handleBrowserException = this.handleBrowserException.bind(this);
    }

    handleBrowserException(event) {
        throw new Error('Warning: Each child in a list should have a unique key prop');
    }

    render() {
        return (
            <Grid container spacing={2}>
                <Box width="100%"><Button variant="contained" data-transaction-name="ErrorLocal" onClick={this.handleBrowserException} type="submit">Submit</Button></Box>
            </Grid>
        );
    }
}

export default ErrorLocal;