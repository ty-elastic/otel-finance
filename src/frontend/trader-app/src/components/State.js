import React, { useState, useEffect } from 'react';
import axios from "axios";

function State({ key }) {
    const [loadingData, setLoadingData] = useState(true);
    const [data, setData] = useState([]);

    useEffect(() => {
        async function getData() {
            await axios
                .get('/monkey/state')
                .then((response) => {
                    // check if the data is populated
                    console.log(response.data);
                    setData(response.data);
                    // you tell it that you had the result
                    setLoadingData(false);
                });
        }
        if (loadingData) {
            // if the result is not ready so you make the axios call
            getData();
        }
    }, []);

    return (
        <div>
            {/* here you check if the state is loading otherwise if you wioll not call that you will get a blank page because the data is an empty array at the moment of mounting */}
            {loadingData ? (
                <p>Loading Please wait...</p>
            ) : (
                <div><pre>{ JSON.stringify(data[key], null, 2) }</pre></div>
            )}
        </div>
    );
}

export default State;