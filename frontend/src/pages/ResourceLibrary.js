import React from 'react';
import './ResourceLibrary.css'; // Import your CSS

const ResourceLibrary = () => {
  const books = [
    {
      id: 1,
      title: "The Great Gatsby",
      author: "F. Scott Fitzgerald",
      description:
        "A classic American novel set in the Jazz Age, exploring themes of wealth, love, and the American Dream.",
      thumbnail: "https://covers.openlibrary.org/b/id/8225261-L.jpg",
      url: "https://www.gutenberg.org/files/64317/64317-h/64317-h.htm",
    },
    {
      id: 2,
      title: "To Kill a Mockingbird",
      author: "Harper Lee",
      description:
        "A powerful story of racial injustice and childhood innocence in the American South.",
      thumbnail: "https://covers.openlibrary.org/b/id/8226934-L.jpg",
      url: "https://archive.org/details/ToKillAMockingbird_201608",
    },
    {
      id: 3,
      title: "1984",
      author: "George Orwell",
      description:
        "A dystopian novel about totalitarianism, surveillance, and the power of language.",
      thumbnail: "https://covers.openlibrary.org/b/id/7222246-L.jpg",
      url: "https://www.gutenberg.org/files/61/61-h/61-h.htm",
    },
  ];

  // Safer window.open (prevents reverse tabnabbing)
  const handleBookClick = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="resource-library">
      <div className="container">
        {/* Header */}
        <header className="header">
          <h1>📚 Resource Library</h1>
          <p>Discover great literature with our curated collection</p>
        </header>

        {/* Books Grid */}
        <div className="books-grid">
          {books.map((book) => (
            <div key={book.id} className="book-card">
              {/* Thumbnail Section */}
              <div
                className="thumbnail-container"
                onClick={() => handleBookClick(book.url)}
                onKeyDown={(e) => e.key === 'Enter' && handleBookClick(book.url)}
                role="button"
                tabIndex={0}
                aria-label={`Open ${book.title}`}
              >
                <img
                  src={book.thumbnail}
                  alt={`Cover of ${book.title}`}
                  className="thumbnail"
                />
                <div className="overlay">
                  <span className="overlay-icon">📖</span>
                </div>
              </div>

              {/* Book Details */}
              <div className="book-details">
                <h3>{book.title}</h3>
                <p className="author">by {book.author}</p>
                <p className="description">{book.description}</p>
                <button
                  onClick={() => handleBookClick(book.url)}
                  className="read-btn"
                  aria-label={`Read ${book.title} now`}
                >
                  Read Now
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <footer className="footer">
          <p>
            📖 Click on any book thumbnail or the <strong>“Read Now”</strong> button to open the book in a new tab.
          </p>
        </footer>
      </div>
    </div>
  );
};

export default ResourceLibrary;
