import * as React from 'react';
import axios from "axios";
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import Box from '@mui/material/Box';

class MarketReset extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            await axios.post(`/monkey/reset/market`);
        } catch (err) {
            console.log(err.message)
        }
        window.location.reload();
    }

    render() {
        return (
            <form name="market_reset" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                <Box width="100%"><Button variant="contained" data-transaction-name="MarketReset" type="submit">Reset</Button></Box>
                </Grid>
            </form>
        );
    }
}

export default MarketReset;