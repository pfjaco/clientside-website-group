import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.

export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerUrl, setOwnerUrl] = useState("");
  const [ownerProfilePicture, setOwnerProfilePicture] = useState("");
  const [likes, setLikes] = useState(-1);
  const [comments, setComments] = useState([]);
  const [postUrl, setPostUrl] = useState("");
  const [niceTime, setNiceTime] = useState("");
  const [likeUnlike, setLikeUnlike] = useState(false);
  const [postid, setPostid] = useState(0);
  const [likeidUrl, setLikeidUrl] = useState("");
  const [commentsLength, setCommentsLength] = useState(-1);
  const loggedInUser = document.getElementById("loggedInUser").text;
  const [userComment, setUserComment] = useState("");
  let localTime = "";

  function deleteComment(commentUrl) {
    const updatedUrl = `/api/v1/posts/${postid}/`;
    fetch(commentUrl, { method: "DELETE", credentials: "same-origin" }).then(
      (response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }

        fetch(updatedUrl, { credentials: "same-origin" })
          .then((newResponse) => {
            if (!newResponse.ok) {
              throw Error(newResponse.statusText);
            }

            return newResponse.json();
          })
          .then(() => {
            setComments(comments.filter((c) => c.url !== commentUrl));
            setCommentsLength(comments.length);
          })
          .catch((error) => console.log(error));
      },
    );
  }

  function addComment(commentText) {
    const commentUrl = `/api/v1/comments/?postid=${postid}`;
    fetch(commentUrl, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: commentText }),
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }

        const updatedUrl = `/api/v1/posts/${postid}/`;
        fetch(updatedUrl, { credentials: "same-origin" })
          .then((newResponse) => {
            if (!newResponse.ok) {
              throw Error(newResponse.statusText);
            }

            return newResponse.json();
          })
          .then((data) => {
            setComments([...comments, data.comments[data.comments.length - 1]]);
            setCommentsLength(comments.length);
          });
      })
      .catch((error) => console.log(error));
  }

  const updateComment = (e) => {
    setUserComment(e.target.value);
  };

  const submitForm = (e) => {
    setUserComment(e.target.value);
    addComment(userComment);
    setUserComment("");
    e.preventDefault();
  };

  function likeImage() {
    const updatedUrl = `/api/v1/posts/${postid}/`;

    if (!likeUnlike) {
      const postUrl2 = `/api/v1/likes/?postid=${postid}`;
      fetch(postUrl2, { method: "POST", credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) {
            throw Error(response.statusText);
          }

          fetch(updatedUrl, { credentials: "same-origin" })
            .then((newResponse) => {
              if (!newResponse.ok) {
                throw Error(newResponse.statusText);
              }

              return newResponse.json();
            })
            .then((newData) => {
              setLikes(newData.likes.numLikes);
              setLikeUnlike(newData.likes.lognameLikesThis);
              setLikeidUrl(newData.likes.url);
            });
        })
        .catch((error) => console.log(error));
    }
  }

  function changeLikeUnlike() {
    const updatedUrl = `/api/v1/posts/${postid}/`;
    if (likeUnlike) {
      fetch(likeidUrl, { method: "DELETE", credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) {
            throw Error(response.statusText);
          }

          fetch(updatedUrl, { credentials: "same-origin" })
            .then((newResponse) => {
              if (!newResponse.ok) {
                throw Error(newResponse.statusText);
              }

              return newResponse.json();
            })
            .then((newData) => {
              setLikes(newData.likes.numLikes);
              setLikeUnlike(newData.likes.lognameLikesThis);
              setLikeidUrl(newData.likes.url);
            });
        })
        .catch((error) => console.log(error));
    } else {
      const postUrl3 = `/api/v1/likes/?postid=${postid}`;
      fetch(postUrl3, { method: "POST", credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) {
            throw Error(response.statusText);
          }

          fetch(updatedUrl, { credentials: "same-origin" })
            .then((newResponse) => {
              if (!newResponse.ok) {
                throw Error(newResponse.statusText);
              }

              return newResponse.json();
            })
            .then((newData) => {
              setLikes(newData.likes.numLikes);
              setLikeUnlike(newData.likes.lognameLikesThis);
              setLikeidUrl(newData.likes.url);
            });
        })
        .catch((error) => console.log(error));
    }
  }

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }

        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setOwnerProfilePicture(data.ownerImgUrl);
          setOwnerUrl(data.ownerShowUrl);
          setComments([...comments, ...data.comments.map((c) => c)]);
          setLikes(data.likes.numLikes);
          setPostUrl(data.postShowUrl);
          localTime = dayjs.utc(data.created).local().format();
          setNiceTime(dayjs(localTime).fromNow());
          setLikeUnlike(data.likes.lognameLikesThis);
          setPostid(data.postid);
          setLikeidUrl(data.likes.url);
          setCommentsLength(comments.length);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const commentOutput = comments.map((c) => (
    <div key={c.commentid}>
      <span data-testid="comment-text">
        <a href={c.ownerShowUrl}>{c.owner}</a> {c.text}
        <br />
      </span>
      {loggedInUser === c.owner ? (
        <button
          type="submit"
          onClick={() => deleteComment(c.url)}
          data-testid="delete-comment-button"
        >
          Delete Comment
        </button>
      ) : (
        ""
      )}
    </div>
  ));

  // Render post image and post owner
  return (
    <>
      <div className="header">
        {postUrl === "" ||
        niceTime === "" ||
        ownerUrl === "" ||
        ownerProfilePicture === "" ||
        owner === "" ? (
          <p>Loading...</p>
        ) : (
          <div className="loadedContent">
            <p>
              <a href={ownerUrl}>
                <img src={ownerProfilePicture} alt="user profile diagram" />
              </a>
            </p>
            <p>
              <a href={ownerUrl}>{owner}</a>
            </p>

            <p>
              <a href={postUrl}> {niceTime}</a>
            </p>
          </div>
        )}
      </div>

      <div className="post">
        {imgUrl === "" ? (
          <p>Loading...</p>
        ) : (
          <img onDoubleClick={likeImage} src={imgUrl} alt="post diagram" />
        )}
      </div>

      <div className="likes">
        {(() => {
          if (likes === -1) return <p>Loading...</p>;
          if (likes === 1) return <p>{likes} like</p>;
          return <p>{likes} likes</p>;
        })()}

        {likes === -1 ? (
          <p>Loading...</p>
        ) : (
          <button
            type="submit"
            value={likeUnlike ? "Unlike" : "Like"}
            data-testid="like-unlike-button"
            onClick={changeLikeUnlike}
          >
            {likeUnlike ? "Unlike" : "Like"}
          </button>
        )}
      </div>

      <div className="comments">
        {commentsLength === -1 ? <p>Loading...</p> : commentOutput}
        {commentsLength === -1 ? (
          <p>Loading...</p>
        ) : (
          <form data-testid="comment-form" onSubmit={submitForm}>
            <input
              type="text"
              value={userComment}
              onChange={updateComment}
              required
            />
          </form>
        )}
      </div>
    </>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

/*
onKeyDown={(e) => {
                if (e.key === "Enter") {
                  if (e.target.value !== null && e.target.value !== "") {
                    addComment(e.target.value);
                    e.preventDefault();
                    e.target.value = ""; // clear the input field once user enters
                  }
                }
              }}
*/
