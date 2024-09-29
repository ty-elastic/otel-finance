import React, { useState, useEffect } from 'react';
import axios from "axios";

function Tester() {

    const handleBrowserException = async () => {
        throw new Error('Intentional Exception!');
    }

    const handleStore404 = async () => {
        try {
            await axios.get("/store/albums", {
                params: {'error': '404'}
            })
        } catch (err) {
            console.log(err.message)
        }
    }    

    const handleStore500 = async () => {
        try {
            await axios.get("/store/albums", {
                params: {'error': '500'}
            })
        } catch (err) {
            console.log(err.message)
        }
    }    

    const handleCatalog401= async () => {
        try {
            await axios.get("/store/albums", {
                params: {'error': 'remote401'}
            })
        } catch (err) {
            console.log(err.message)
        }
    }   
    
    const handleCatalogLatency= async () => {
        try {
            await axios.get("/store/albums", {
                params: {'error': 'remoteLatency'}
            })
        } catch (err) {
            console.log(err.message)
        }
    }  

    return (
            <div>
                <button type="submit" onClick={handleBrowserException} >Browser Exception</button>
                <button type="submit" onClick={handleStore404} >Store:404</button>
                <button type="submit" onClick={handleStore500} >Store:500</button>
                <button type="submit" onClick={handleCatalog401} >Catalog:401</button>
                <button type="submit" onClick={handleCatalogLatency} >Catalog:Latency</button>
            </div>
    )
}

export default Tester;