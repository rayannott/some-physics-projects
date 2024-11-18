import pytest

import smart


@pytest.mark.parametrize(["a", "b"], [(1, 2), ('one', 'zwei'), (1.5, 2.5)])
def test_add(a, b):
    completion = smart.client.chat.completions.create(
        model=smart.MODEL,
        messages=[
            {"role": "system", "content": "You are a mathematics teacher."},
            {
                "role": "user",
                "content": f"Do you know what {a} + {b} is? Don't give the result, just say 'yes' or 'no'.",
            },
        ],
    )
    resp = completion.choices[0].message.content
    assert resp
    assert "yes" in resp.lower()
