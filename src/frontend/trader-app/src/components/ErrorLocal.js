import * as React from 'react';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

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
            <Stack
                direction="column"
                spacing={1}
                sx={{
                    justifyContent: "flex-start",
                    alignItems: "flex-start",
                }}
            >
                <Button variant="contained" data-transaction-name="ErrorLocal" type="submit" onClick={this.handleBrowserException}>Browser Exception</Button>
            </Stack>
        );
    }
}

export default ErrorLocal;