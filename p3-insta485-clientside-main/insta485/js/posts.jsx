import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function Posts({ url }) {
  const [postData, setPostData] = useState([]);
  const [next, setNext] = useState("");
  const [postsLength, setPostsLength] = useState(-1);

  function getMoreData() {
    fetch(next, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }

        return response.json();
      })
      .then((data) => {
        setPostData([...postData, ...data.results.map((p) => p)]);
        setNext(data.next);
        setPostsLength(postData.length);
      })
      .catch((error) => console.log(error));
  }

  useEffect(() => {
    let ignoreStaleRequest = false;

    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }

        return response.json();
      })

      .then((data) => {
        if (!ignoreStaleRequest) {
          setPostData([...postData, ...data.results.map((p) => p)]);
          setNext(data.next);
          setPostsLength(postData.length);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      ignoreStaleRequest = true;
    };
  }, [url]);

  return (
    <InfiniteScroll
      dataLength={postData.length}
      next={() => {
        getMoreData();
      }}
      hasMore={next !== ""}
      loader={<p>Loading...</p>}
    >
      {postsLength === -1 ? (
        <p>Loading...</p>
      ) : (
        postData.map((p) => (
          <div key={p.postid}>
            <Post url={p.url} />
          </div>
        ))
      )}
    </InfiniteScroll>
  );
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};
