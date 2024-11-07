import * as React from 'react';
import axios from "axios";
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import Box from '@mui/material/Box';

class ErrorReset extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            await axios.post(`/monkey/reset/error`);
        } catch (err) {
            console.log(err.message)
        }
        window.location.reload();
    }

    render() {
        return (
            <form name="error_reset" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                    <Box width="100%"><Button variant="contained" data-transaction-name="ErrorReset" type="submit">Reset</Button></Box>
                </Grid>
            </form>
        );
    }
}

export default ErrorReset;