import React, { useState, useEffect } from 'react';
import axios from "axios";

function AlbumList() {
    const [loadingData, setLoadingData] = useState(true);
    const [data, setData] = useState([]);

    useEffect(() => {
        async function getData() {
          await axios
            .get('/store/albums')
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

      const renderTableData = () => {
        return data?.map((val) => (
          <tr key={val.id}>
            <td>{val.id}</td>
            <td>{val.title}</td>
            <td>{val.artist}</td>
            <td>{val.price}</td>
          </tr>
        ));
      };

    return (
        <div className="AlbumList">
          {/* here you check if the state is loading otherwise if you wioll not call that you will get a blank page because the data is an empty array at the moment of mounting */}
          {loadingData ? (
            <p>Loading Please wait...</p>
          ) : (
                <table id="table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Artist</th>
                      <th>Price</th>
                    </tr>
                  </thead>
                  <tbody>{renderTableData()}</tbody>
                </table>
          )}
        </div>
      );
}

export default AlbumList;