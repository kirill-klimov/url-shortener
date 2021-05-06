const LinkEditForm = (short_id, visibility) => {
  const form = document.createElement('form')
  form.classList.add('edit-form')
  form.addEventListener('submit', (e) => {
    e.preventDefault()
    const target = e.target[0].target_id
    const short_id = e.target[0].value.trim()
    const visibility = e.target[1].value.trim()
    updateLink(target, { short_id, visibility });
  })

  const linkInput = document.createElement('input')
  linkInput.type = "text"
  linkInput.name = "link"
  linkInput.value = short_id
  linkInput.target_id = short_id
  linkInput.placeholder = "Длинная ссылка"

  const label = document.createElement('label')
  label.textContent = "Доступность"
  
  const select = document.createElement('select')

  const option1 = document.createElement('option')
  option1.value = "public"
  option1.textContent = "Публичная"
  option1.selected = visibility === option1.value

  const option2 = document.createElement('option')
  option2.value = "auth"
  option2.textContent = "Только авторизованным"
  option2.selected = visibility === option2.value

  const option3 = document.createElement('option')
  option3.value = "private"
  option3.textContent = "Только мне"
  option3.selected = visibility === option3.value

  select.appendChild(option1)
  select.appendChild(option2)
  select.appendChild(option3)

  label.appendChild(select)

  const div = document.createElement('div')
  div.classList.add("edit-form__controls")

  const cancelButton = document.createElement('button')
  cancelButton.type = "button"
  cancelButton.textContent = "Отмена"
  cancelButton.addEventListener('click', () => form.classList.remove('flex'))

  const saveButton = document.createElement('button')
  saveButton.type = "submit"
  saveButton.textContent = "Сохранить"
  
  div.appendChild(cancelButton)
  div.appendChild(saveButton)

  form.appendChild(linkInput)
  form.appendChild(label)
  form.appendChild(div)

  return form;
} 

const Link = (url, {visibility, counter, short_id}) => {
  const editForm = LinkEditForm(short_id, visibility)
  const li = document.createElement('li')

  const link = document.createElement('a')
  link.href = url;
  link.textContent = url;
  link.target = "_blank";

  li.appendChild(link)

  const visibilityDict = {
    public: 'Публичная',
    auth: 'Только авторизованным',
    private: 'Только мне'
  }

  const visibilitySpan = document.createElement('span')
  visibilitySpan.textContent = ` [${visibilityDict[visibility]}]`
  li.appendChild(visibilitySpan)

  const counterSpan = document.createElement('span')
  counterSpan.textContent = ` [${counter}]`
  li.appendChild(counterSpan)

  const editBtn = document.createElement('button')
  const editIcon = document.createElement('img')
  editIcon.src = "/static/edit.svg"
  editBtn.appendChild(editIcon)
  editBtn.style.marginLeft = "10px"
  editBtn.addEventListener('click', () => editForm.classList.toggle('flex'))

  li.appendChild(editBtn)

  const deleteBtn = document.createElement('button')
  const deleteIcon = document.createElement('img')
  deleteIcon.src = "/static/trash.svg"
  deleteBtn.appendChild(deleteIcon)
  deleteBtn.style.marginLeft = "4px"
  deleteBtn.addEventListener('click', () => deleteLink(short_id))

  li.appendChild(deleteBtn)

  li.appendChild(editForm)

  return li;
}

document.getElementById("short-form")
.addEventListener('submit', async (e) => {
  e.preventDefault()

  const longUrl = e.target[0].value.trim();
  if (!longUrl.length) return;
  const { url } = await (await fetch('/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url: longUrl })
  })).json();
  
  const link = document.getElementById("link-span")
  link.textContent = url
  link.href = url
  
  e.target[0].value = ''
  fetchUserLinks();
})


const fetchUserLinks = async () => {
  const res = await fetch('/me')
  const links = await res.json();
  const linkList = document.getElementById("user-links")
  if (!links.length) {
    linkList.innerHTML = ''
    linkList.textContent = 'Пусто'
  } else {
    linkList.innerHTML = ''
    links.forEach(link => {
      const url = `${window.location.origin}/${link.short_id}`;
      linkList.appendChild(Link(url, link))
    });
  }
}

fetchUserLinks()

const deleteLink = async (short_id) => {
  const url = '/' + short_id
  await fetch(url, { method: 'DELETE' })
  fetchUserLinks()
}

const updateLink = async (target, {short_id, visibility}) => {
  const url = '/' + target
  await fetch(url, {
    method: 'UPDATE',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({short_id, visibility})
  })
  fetchUserLinks()
}