import * as React from 'react';
import axios from "axios";

import MonkeyState from './MonkeyState'
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';

class CanaryRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            canary_region_on: false,
            canary_region: 'EU'
        };

        this.monkeyState = new MonkeyState(this, 'canary_per_region');

        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value
        });
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            if (this.state.canary_region_on === false) {
                await axios.delete(`/monkey/canary/region/${this.state.canary_region}`);
            } else {
                await axios.post(`/monkey/canary/region/${this.state.canary_region}`);
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form name="canary_region" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                    <FormGroup>
                        <FormControlLabel control={<Checkbox
                            name='canary_region_on'
                            checked={this.state.canary_region_on}
                            onChange={this.handleInputChange}
                            inputProps={{ 'aria-label': 'controlled' }}
                        />} label="Canary" />
                    </FormGroup>
                    <FormControl>
                        <InputLabel id="label_region">Region</InputLabel>
                        <Select
                            labelId="label_region"
                            name="canary_region"
                            value={this.state.canary_region}
                            label="Region"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="EMEA">EMEA</MenuItem>
                            <MenuItem value="EU">EU</MenuItem>
                            <MenuItem value="LATAM">LATAM</MenuItem>
                            <MenuItem value="NA">NA</MenuItem>
                        </Select>
                    </FormControl>
                    <Box width="100%"><Button variant="contained" data-transaction-name="CanaryRegion" type="submit">Submit</Button></Box>
                    {this.monkeyState.render()}
                </Grid>
            </form>
        );
    }
}

export default CanaryRegion;