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
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';

class ErrorModelRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            err_model_region_on: false,
            err_model_region: 'EU'
        };

        this.monkeyState = new MonkeyState(this, 'model_error_per_region');

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
                await axios.delete(`/monkey/err/model/region/${this.state.err_model_region}`);
            } else {
                await axios.post(`/monkey/err/model/region/${this.state.err_model_region}/100`);
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (

            <form name="err_model_region" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                    <FormControl>
                        <InputLabel id="label_region">Region</InputLabel>
                        <Select
                            labelId="label_region"
                            name="err_model_region"
                            value={this.state.err_model_region}
                            label="Region"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="EMEA">EMEA</MenuItem>
                            <MenuItem value="EU">EU</MenuItem>
                            <MenuItem value="LATAM">LATAM</MenuItem>
                            <MenuItem value="NA">NA</MenuItem>
                        </Select>
                    </FormControl>
                    <FormGroup>
                        <FormControlLabel control={<Checkbox
                            name='err_model_region_on'
                            checked={this.state.err_model_region_on}
                            onChange={this.handleInputChange}
                            inputProps={{ 'aria-label': 'controlled' }}
                        />} label="Generate errors" />
                    </FormGroup>
                    <Box width="100%"><Button variant="contained" data-transaction-name="ErrorModelRegion" type="submit">Submit</Button></Box>
                    {this.monkeyState.render()}
                </Grid>
            </form>
        );
    }
}

export default ErrorModelRegion;