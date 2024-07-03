# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Main",
        page_icon="👋",
    )

    st.write("# Welcome to ALM Risk! 👋")

    st.sidebar.success("Select a page above.")

    st.markdown(
        """
        **👈 Select a page from the sidebar** to see some examples!

        - **Banks Capital** - list of banks by capital value from the Bank of Russia website.
        - **Banks Capital chart** - chart of banks capital since 2011
        - **Banks PnL chart** - chart of banks PnL since 2012
    """
    )


if __name__ == "__main__":
    run()
