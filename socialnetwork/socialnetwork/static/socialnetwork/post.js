"use strict"

function getList(type) {
    let endpoint = type === 'follower' ? "socialnetwork/get-follower" : "socialnetwork/get-global";
    
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return;
        updatePage(xhr, type);
    }

    xhr.open("GET", endpoint, true);
    xhr.send();
}

function updatePage(xhr, type) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updateList(response, type)
        return
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function displayError(message, id = null) {
    let errorElementId = id ? `error_${id}` : `error`;
    let errorElement = document.getElementById(errorElementId);
    if (errorElement) {
        errorElement.innerHTML = message;
    }
}

function updateList(items, type) {
    let list = document.getElementById("all-posts");

    items.posts.forEach(post => {
        let postElement = document.getElementById(`id_post_div_${post.id}`);

        if (!postElement) {
            postElement = makeListItemElement(post, [], type);
            list.prepend(postElement);
        }

        const currentComments = Array.from(postElement.getElementsByClassName("comment"));
        const currentCommentIds = currentComments.map(commentDiv => {
            return parseInt(commentDiv.id.replace("id_comment_div_", ""), 10);
        });

        items.comments
            .filter(comment => comment.post === post.id && !currentCommentIds.includes(comment.id))
            .forEach(comment => {
                const commentMarkup = generateCommentMarkup(comment, post.user_id);
                const div = document.createElement("div");
                div.innerHTML = commentMarkup.trim();
                postElement.insertBefore(div.firstChild, postElement.querySelector(".new_comment"));
            });
    });
}

function convertIsoToLocalDateTime(isoStr) {
    let dateObj = new Date(isoStr);
    
    let month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    let day = dateObj.getDate().toString().padStart(2, '0');
    let year = dateObj.getFullYear();

    let hours = dateObj.getHours();
    let ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    let minutes = dateObj.getMinutes().toString().padStart(2, '0');

    return `${month}/${day}/${year} ${hours}:${minutes} ${ampm}`;
}

function generateProfileLink(userId, name, idSuffix) {
    return `<a class="profile-link" href="${profileURL(userId)}" id="${idSuffix}">${name}</a>`;
}

function generatePostMarkup(post) {
    const profile = generateProfileLink(post.user_id, `${post.fname} ${post.lname}`, `id_post_profile_${post.id}`);
    return `
        Post by ${profile} -
        <span class="cp-text" id="id_post_text_${post.id}">${sanitize(post.text)}</span> - 
        <span class="date" id="id_post_date_time_${post.id}">${convertIsoToLocalDateTime(post.post_date)}</span>
    `;
}

function generateCommentMarkup(comment) {
    const profile = generateProfileLink(comment.user_id, `${comment.fname} ${comment.lname}`, `id_comment_profile_${comment.id}`);
    return `
        <div class="comment" id="id_comment_div_${comment.id}">
            Comment by ${profile} -
            <span class="cp-text" id="id_comment_text_${comment.id}"> ${sanitize(comment.text)}</span> -
            <span class="date" id="id_comment_date_time_${comment.id}"> ${convertIsoToLocalDateTime(comment.creation_time)}</span>
            <span id="error_${comment.id}" class="error"></span>
        </div>
    `;
}

function makeListItemElement(post, allComments, type) {
    const commentsForPost = allComments.filter(comment => comment.post === post.id);
    const comments = commentsForPost.map(comment => generateCommentMarkup(comment, post.user_id)).join('');

    const newCommentMarkup = `
        <div class="new_comment">
            <label for="new_comment_text_${post.id}">Comment:</label>
            <input id="id_comment_input_text_${post.id}" type="text" name="comment" autofocus />
            <button id="id_comment_button_${post.id}" type="submit" onclick="addItem(${post.id}, '${type}')">Submit</button>
        </div>
    `;

    const element = document.createElement("div");
    element.setAttribute("id", `id_post_div_${post.id}`);
    element.setAttribute("class", "post");
    element.innerHTML = `
        ${generatePostMarkup(post)}
        <br> 
        ${comments}
        <br> 
        ${newCommentMarkup}
    `;
    
    return element;
}

function sanitize(s) {
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addItem(id, type) {
    let itemTextElement = document.getElementById(`id_comment_input_text_${id}`)
    let itemTextValue   = itemTextElement.value

    itemTextElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return;

        if (xhr.status !== 200) {
            let response = JSON.parse(xhr.responseText);
            displayError(response.error || "An error occurred", id);
        } else {
            updatePage(xhr);
        }
    };

    xhr.open("POST", addItemURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`comment_text=${itemTextValue}&post_id=${id}&type=${type}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}
