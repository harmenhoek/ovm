var mod = new bootstrap.Modal(document.getElementById("modalhtmx"))

htmx.on("htmx:afterSwap", (e) => {
  // Response targeting #dialog => show the modal
  if (e.detail.target.id === "dialoghtmx") {
    mod.show()
  }
})

htmx.on("htmx:beforeSwap", (e) => {
  // Empty response targeting #dialog => hide the modal
  if (e.detail.target.id === "dialoghtmx" && !e.detail.xhr.response) {
    mod.hide()
    e.detail.shouldSwap = false
  }
})

htmx.on("hidden.bs.modal", () => {
  document.getElementById("dialoghtmx").innerHTML = ""
})

